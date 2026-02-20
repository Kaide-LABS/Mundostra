"""Orchestrator Engine — the brain of the multi-agent system.

Handles event intake, parallel agent dispatch, result synthesis, and confidence gating.
"""

from __future__ import annotations

import asyncio
import json
import time
from typing import Any
from uuid import UUID

import httpx

from backend.agents.comms import CommsAgent
from backend.agents.policy import PolicyAgent
from backend.agents.research import ResearchAgent
from backend.config import get_settings
from backend.gmail.sender import GmailSender
from backend.logging_config import get_logger
from backend.message_bus.bus import MessageBus
from backend.models.events import TravelEvent
from backend.models.resolutions import (
    CommsResult,
    FlightAlternative,
    PolicyEvaluation,
    PolicyResult,
    ResearchResult,
    Resolution,
    ResolutionStatus,
)
from backend.models.tasks import (
    AgentName,
    AgentTask,
    TaskStatus,
    TraceStatus,
)
from backend.orchestrator.prompts import (
    ORCHESTRATOR_PLANNING_PROMPT,
    ORCHESTRATOR_SYNTHESIS_PROMPT,
    ORCHESTRATOR_SYSTEM_PROMPT,
)

logger = get_logger(__name__)


class OrchestratorEngine:
    """Core orchestration logic.

    handle_event() is the main entry point:
    1. Planning phase — decompose event into agent tasks
    2. Parallel dispatch — Research + Policy agents run concurrently
    3. Synthesis — merge results, assign confidence score
    4. Action — if confidence >= threshold, dispatch Comms agent; else escalate
    """

    def __init__(
        self,
        bus: MessageBus,
        http_transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.bus = bus
        self.settings = get_settings()
        self.resolutions: dict[UUID, Resolution] = {}

        # Conditionally create Gmail sender
        self.gmail_sender: GmailSender | None = None
        if (
            self.settings.gmail_enabled
            and self.settings.gmail_sender
            and self.settings.gmail_app_password
            and self.settings.gmail_recipient
        ):
            self.gmail_sender = GmailSender(
                sender_email=self.settings.gmail_sender,
                app_password=self.settings.gmail_app_password,
                recipient_email=self.settings.gmail_recipient,
            )

        agent_kwargs: dict[str, Any] = {
            "bus": bus,
            "mock_llm": self.settings.mock_llm,
            "base_url": self.settings.base_url,
            "http_transport": http_transport,
        }
        self.research_agent = ResearchAgent(**agent_kwargs)
        self.policy_agent = PolicyAgent(**agent_kwargs)
        self.comms_agent = CommsAgent(gmail_sender=self.gmail_sender, **agent_kwargs)

    async def handle_event(self, event: TravelEvent) -> Resolution:
        start = time.monotonic()
        event_id = event.id

        await self._emit(event_id, TraceStatus.THINKING, "Event received. Classifying...")

        # Phase 1: Planning
        plan = await self._plan(event)
        await self._emit(
            event_id,
            TraceStatus.WORKING,
            "Dispatching Research + Policy agents in parallel",
            data=plan,
        )

        # Phase 2: Parallel dispatch of Research + Policy
        research_task = AgentTask(
            event_id=event_id,
            agent=AgentName.RESEARCH,
            input_data={
                "flight": event.flight.model_dump(mode="json") if event.flight else {},
                "traveler": event.traveler.model_dump(mode="json"),
            },
        )

        policy_task = AgentTask(
            event_id=event_id,
            agent=AgentName.POLICY,
            input_data={
                "flight": event.flight.model_dump(mode="json") if event.flight else {},
                "traveler": event.traveler.model_dump(mode="json"),
                "alternatives": [],  # Will be populated after research for real LLM
            },
        )

        # Run in parallel — both complete even if one fails
        research_result_task, policy_result_task = await asyncio.gather(
            self.research_agent.execute(research_task),
            self.policy_agent.execute(policy_task),
            return_exceptions=False,
        )

        # If research succeeded, re-run policy with alternatives for accurate evaluation
        research_output = research_result_task.output_data or {}
        alternatives = research_output.get("alternatives", [])

        if alternatives and policy_result_task.status == TaskStatus.COMPLETE:
            # Re-evaluate policy with actual alternatives
            policy_reeval_task = AgentTask(
                event_id=event_id,
                agent=AgentName.POLICY,
                input_data={
                    "flight": event.flight.model_dump(mode="json") if event.flight else {},
                    "traveler": event.traveler.model_dump(mode="json"),
                    "alternatives": alternatives,
                },
            )
            policy_result_task = await self.policy_agent.execute(policy_reeval_task)

        policy_output = policy_result_task.output_data or {}

        # Phase 3: Synthesis
        await self._emit(event_id, TraceStatus.WORKING, "Synthesizing agent results...")

        synthesis = await self._synthesize(event, research_output, policy_output)
        confidence = synthesis.get("confidence_score", 0.0)

        await self._emit(
            event_id,
            TraceStatus.WORKING,
            f"Confidence: {confidence:.2f}",
            data=synthesis,
        )

        # Build resolution
        research_result = self._build_research_result(research_output)
        policy_result = self._build_policy_result(policy_output)
        chosen_option = self._pick_chosen_option(synthesis, research_output)

        resolution = Resolution(
            event_id=event_id,
            confidence_score=confidence,
            policy_compliant=synthesis.get("policy_compliant", False),
            chosen_option=chosen_option,
            research_result=research_result,
            policy_result=policy_result,
            agents_involved=["orchestrator", "research", "policy"],
        )

        # Phase 4: Confidence gating
        if confidence >= self.settings.confidence_threshold and chosen_option:
            await self._emit(
                event_id,
                TraceStatus.WORKING,
                f"Confidence {confidence:.2f} >= {self.settings.confidence_threshold}. Dispatching Comms agent.",
            )

            comms_task = AgentTask(
                event_id=event_id,
                agent=AgentName.COMMS,
                input_data={
                    "traveler": event.traveler.model_dump(mode="json"),
                    "chosen_option": chosen_option.model_dump(mode="json"),
                    "confidence_score": confidence,
                    "auto_approved": synthesis.get("auto_approved", True),
                    "cancelled_flight": event.flight.number if event.flight else "",
                    "origin": event.flight.origin if event.flight else "",
                    "destination": event.flight.destination if event.flight else "",
                },
            )
            comms_result_task = await self.comms_agent.execute(comms_task)

            if comms_result_task.status == TaskStatus.COMPLETE and comms_result_task.output_data:
                resolution.comms_result = CommsResult(**comms_result_task.output_data)
                resolution.agents_involved.append("comms")

            resolution.status = ResolutionStatus.PROPOSED

            # Calculate costs
            resolution.total_cost_usd = (
                research_result_task.cost_usd
                + policy_result_task.cost_usd
                + comms_result_task.cost_usd
            )
        else:
            await self._emit(
                event_id,
                TraceStatus.ESCALATION,
                f"Confidence {confidence:.2f} < {self.settings.confidence_threshold}. Escalating to human.",
            )
            resolution.status = ResolutionStatus.ESCALATED
            resolution.total_cost_usd = research_result_task.cost_usd + policy_result_task.cost_usd

        elapsed = time.monotonic() - start
        resolution.total_time_seconds = elapsed

        status_msg = "RESOLVED" if resolution.status == ResolutionStatus.PROPOSED else "ESCALATED"
        await self._emit(
            event_id,
            TraceStatus.COMPLETE,
            f"{status_msg} — {elapsed:.1f} seconds, ${resolution.total_cost_usd:.4f} total API cost",
        )

        self.resolutions[event_id] = resolution
        return resolution

    async def _plan(self, event: TravelEvent) -> dict[str, Any]:
        """Phase 1: Use orchestrator LLM to decompose event (or mock)."""
        if self.settings.mock_llm:
            return {
                "assessment": {
                    "event_type": event.event_type.value,
                    "urgency": "high",
                    "affected_traveler": event.traveler.name,
                    "key_constraints": [
                        "Board meeting at 10 AM tomorrow",
                        f"Policy tier: {event.traveler.policy_tier.value}",
                        "Calendar integration enabled",
                    ],
                },
                "tasks": [
                    {
                        "agent": "research",
                        "objective": "Find alternative flights and check calendar",
                        "input_summary": f"Route {event.flight.origin}\u2192{event.flight.destination}"
                        if event.flight
                        else "Unknown route",
                    },
                    {
                        "agent": "policy",
                        "objective": "Evaluate policy compliance for alternatives",
                        "input_summary": f"Tier: {event.traveler.policy_tier.value}",
                    },
                ],
            }

        prompt = ORCHESTRATOR_PLANNING_PROMPT.format(
            event_json=event.model_dump_json(indent=2),
        )
        response = await self._call_orchestrator_llm(prompt)
        try:
            return json.loads(response)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            return {"assessment": {"urgency": "high"}, "tasks": []}

    async def _synthesize(
        self,
        event: TravelEvent,
        research_output: dict[str, Any],
        policy_output: dict[str, Any],
    ) -> dict[str, Any]:
        """Phase 3: Merge research + policy results into a decision."""
        if self.settings.mock_llm:
            return self._mock_synthesis(research_output, policy_output)

        prompt = ORCHESTRATOR_SYNTHESIS_PROMPT.format(
            event_json=event.model_dump_json(indent=2),
            research_json=json.dumps(research_output, indent=2),
            policy_json=json.dumps(policy_output, indent=2),
        )
        response = await self._call_orchestrator_llm(prompt)
        try:
            return json.loads(response)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            return self._mock_synthesis(research_output, policy_output)

    def _mock_synthesis(
        self,
        research_output: dict[str, Any],
        policy_output: dict[str, Any],
    ) -> dict[str, Any]:
        """Deterministic synthesis for mock mode."""
        alternatives = research_output.get("alternatives", [])
        evaluations = policy_output.get("policy_evaluation", [])

        # Build set of compliant flights
        compliant_flights = {e["flight"] for e in evaluations if e.get("compliant", False)}

        # Filter: available, no calendar conflict, policy compliant
        viable = [
            a
            for a in alternatives
            if not a.get("calendar_conflict", False)
            and a.get("seat_available", True)
            and (not compliant_flights or a["flight"] in compliant_flights)
        ]

        if not viable:
            viable = [a for a in alternatives if not a.get("calendar_conflict", False)]

        if viable:
            # Sort by price
            viable.sort(key=lambda x: float(x.get("price", 9999)))
            chosen = viable[0]

            # Find matching policy evaluation
            matching_eval = next((e for e in evaluations if e["flight"] == chosen["flight"]), None)
            auto_approved = matching_eval and not matching_eval.get("approval_required", True)

            return {
                "chosen_flight": chosen["flight"],
                "confidence_score": 0.94,
                "reasoning": (
                    f"{chosen['flight']} is the best option: "
                    f"${chosen['price']}, no calendar conflicts, policy compliant"
                ),
                "policy_compliant": True,
                "auto_approved": auto_approved,
                "escalation_needed": False,
            }

        return {
            "chosen_flight": None,
            "confidence_score": 0.3,
            "reasoning": "No viable options found — all alternatives have conflicts or policy issues",
            "policy_compliant": False,
            "auto_approved": False,
            "escalation_needed": True,
        }

    def _build_research_result(self, output: dict[str, Any]) -> ResearchResult:
        alts = []
        for a in output.get("alternatives", []):
            try:
                alts.append(FlightAlternative(**a))
            except Exception:
                continue
        return ResearchResult(
            alternatives=alts,
            recommendation=output.get("recommendation", ""),
            search_metadata=output.get("search_metadata", {}),
        )

    def _build_policy_result(self, output: dict[str, Any]) -> PolicyResult:
        evals = []
        for e in output.get("policy_evaluation", []):
            try:
                evals.append(PolicyEvaluation(**e))
            except Exception:
                continue
        return PolicyResult(
            policy_evaluation=evals,
            auto_approve_eligible=output.get("auto_approve_eligible", False),
            escalation_required=output.get("escalation_required", False),
            policy_version=output.get("policy_version", "v2.3"),
        )

    def _pick_chosen_option(
        self, synthesis: dict[str, Any], research_output: dict[str, Any]
    ) -> FlightAlternative | None:
        chosen_flight = synthesis.get("chosen_flight")
        if not chosen_flight:
            return None
        for a in research_output.get("alternatives", []):
            if a.get("flight") == chosen_flight:
                try:
                    return FlightAlternative(**a)
                except Exception:
                    return None
        return None

    async def _call_orchestrator_llm(self, user_message: str) -> str:
        """Call Claude Opus via Bedrock for orchestration decisions."""
        import boto3

        settings = get_settings()

        def _sync_call() -> str:
            client = boto3.client(
                "bedrock-runtime",
                region_name=settings.aws_region,
            )
            response = client.converse(
                modelId=settings.orchestrator_model_id,
                system=[{"text": ORCHESTRATOR_SYSTEM_PROMPT}],
                messages=[{"role": "user", "content": [{"text": user_message}]}],
                inferenceConfig={"maxTokens": 4096, "temperature": 0.2},
            )
            return response["output"]["message"]["content"][0]["text"]  # type: ignore[no-any-return]

        return await asyncio.to_thread(_sync_call)

    async def _emit(
        self,
        event_id: UUID,
        status: TraceStatus,
        message: str,
        data: dict[str, Any] | None = None,
    ) -> None:
        from backend.models.tasks import AgentTraceEntry

        entry = AgentTraceEntry(
            event_id=event_id,
            agent=AgentName.ORCHESTRATOR,
            model=self.settings.orchestrator_model_id,
            status=status,
            message=message,
            data=data,
        )
        await self.bus.publish(entry)

    def get_resolution(self, event_id: UUID) -> Resolution | None:
        return self.resolutions.get(event_id)

    async def respond_to_event(
        self,
        event_id_str: str,
        response: Any,
    ) -> Resolution | None:
        """Handle a traveler response (confirm / options / reject).

        Called from the REST endpoint.
        """
        from backend.gmail.emails import build_confirmation_email, build_options_email
        from backend.models.responses import TravelerResponseType

        event_id = UUID(event_id_str)
        resolution = self.resolutions.get(event_id)
        if resolution is None:
            return None

        response_type: TravelerResponseType = response.response_type

        if response_type == TravelerResponseType.CONFIRM:
            # If user selected a specific option, swap chosen_option
            selected: int | None = getattr(response, "selected_option", None)
            if selected is not None and resolution.research_result:
                alts = resolution.research_result.alternatives
                idx = selected - 1  # convert 1-based to 0-based
                if 0 <= idx < len(alts):
                    resolution.chosen_option = alts[idx]

            resolution.status = ResolutionStatus.CONFIRMED

            # Authorize virtual card via mock API
            await self._emit(
                event_id,
                TraceStatus.WORKING,
                "Authorizing virtual card for booking...",
            )
            try:
                async with httpx.AsyncClient(base_url=self.settings.base_url) as client:
                    card_resp = await client.post(
                        "/mock/cards/authorize",
                        json={
                            "booking_ref": str(event_id),
                            "amount": resolution.chosen_option.price
                            if resolution.chosen_option
                            else 0,
                            "currency": "USD",
                            "merchant": "airline",
                        },
                    )
                    card_data = card_resp.json()
            except Exception as exc:
                card_data = {"error": str(exc)}

            await self._emit(
                event_id,
                TraceStatus.WORKING,
                f"Card authorized: {card_data.get('card_last_four', '****')}",
                data=card_data,
            )

            await self._emit(
                event_id,
                TraceStatus.COMPLETE,
                f"Booking confirmed — {resolution.chosen_option.flight if resolution.chosen_option else 'N/A'}",
            )

            # Send confirmation email if sender exists
            if self.gmail_sender and resolution.chosen_option:
                try:
                    traveler_name = ""
                    if resolution.comms_result:
                        traveler_name = "Traveler"
                    email = build_confirmation_email(
                        traveler_name=traveler_name,
                        chosen_flight=resolution.chosen_option.flight,
                        departure=str(resolution.chosen_option.departure),
                    )
                    await self.gmail_sender.send_resolution(
                        event_id=event_id_str,
                        email=email,
                    )
                except Exception:
                    pass  # Non-critical — dashboard still reflects confirmation

        elif response_type == TravelerResponseType.OPTIONS:
            # Emit trace with alternatives list, keep status as PROPOSED
            alternatives_data: list[dict[str, Any]] = []
            if resolution.research_result:
                alternatives_data = [
                    a.model_dump(mode="json") for a in resolution.research_result.alternatives
                ]

            await self._emit(
                event_id,
                TraceStatus.WORKING,
                f"Traveler requested options — {len(alternatives_data)} alternatives available",
                data={"alternatives": alternatives_data},
            )

            # Send options email
            if self.gmail_sender:
                try:
                    email = build_options_email(
                        traveler_name="Traveler",
                        alternatives=alternatives_data,
                    )
                    await self.gmail_sender.send_resolution(
                        event_id=event_id_str,
                        email=email,
                    )
                except Exception:
                    pass

        elif response_type == TravelerResponseType.REJECT:
            resolution.status = ResolutionStatus.REJECTED
            await self._emit(
                event_id,
                TraceStatus.ESCALATION,
                "Traveler rejected resolution — escalating to human agent",
            )

        return resolution

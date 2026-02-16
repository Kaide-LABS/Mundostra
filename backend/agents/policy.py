"""Policy Agent — Claude Haiku via AWS Bedrock.

Validates flight alternatives against company travel policy.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from backend.agents.base import BaseAgent
from backend.config import get_settings
from backend.logging_config import get_logger
from backend.models.tasks import AgentName, AgentTask, TraceStatus
from backend.orchestrator.prompts import POLICY_SYSTEM_PROMPT

logger = get_logger(__name__)


def _sanitize_json(text: str) -> str:
    """Extract JSON from LLM response that may contain markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        # Remove first and last lines (fences)
        lines = [line for line in lines[1:] if not line.strip().startswith("```")]
        text = "\n".join(lines)
    return text.strip()


class PolicyAgent(BaseAgent):
    agent_name = AgentName.POLICY

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        settings = get_settings()
        self.model_id = settings.policy_model_id

    async def run(self, task: AgentTask) -> dict[str, Any]:
        event_data = task.input_data
        flight = event_data.get("flight", {})
        traveler = event_data.get("traveler", {})
        alternatives = event_data.get("alternatives", [])

        policy_tier = traveler.get("policy_tier", "standard")
        original_price = flight.get("original_price", 400.0)

        await self.emit_trace(
            event_id=task.event_id,
            status=TraceStatus.WORKING,
            message=f"Checking {policy_tier} tier policy for {len(alternatives)} options...",
        )

        # Query mock policy API for each alternative
        evaluations: list[dict[str, Any]] = []
        any_auto_approve = False
        any_escalation = False

        async with self._make_http_client() as client:
            for alt in alternatives:
                price = float(alt.get("price", 0))
                cabin = alt.get("cabin", "economy")

                policy_resp = await client.get(
                    "/mock/policy/evaluate",
                    params={
                        "policy_tier": policy_tier,
                        "original_price": original_price,
                        "proposed_price": price,
                        "cabin": cabin,
                    },
                )
                policy_data = policy_resp.json()

                within_cap = policy_data.get("within_cap", False)
                auto_eligible = policy_data.get("auto_approve_eligible", False)
                delta = policy_data.get("price_delta", 0)

                if auto_eligible:
                    any_auto_approve = True
                if not within_cap:
                    any_escalation = True

                if within_cap:
                    if auto_eligible:
                        notes = f"Price delta +${delta:.0f} is under auto-approve threshold"
                    else:
                        notes = f"Within budget cap but delta +${delta:.0f} requires approval"
                else:
                    notes = f"Price ${price:.0f} exceeds {policy_tier} tier cap"

                evaluations.append(
                    {
                        "flight": alt.get("flight", ""),
                        "price": price,
                        "budget_status": policy_data.get("budget_status", "within_cap"),
                        "approval_required": not auto_eligible,
                        "policy_notes": notes,
                        "compliant": within_cap,
                    }
                )

        if self.mock_llm:
            task.tokens_used = 524
            task.cost_usd = 0.0004
            return {
                "policy_evaluation": evaluations,
                "auto_approve_eligible": any_auto_approve,
                "escalation_required": any_escalation,
                "policy_version": "v2.3",
            }

        # Real LLM call for additional reasoning
        user_message = (
            f"Policy tier: {policy_tier}\n"
            f"Original booking price: ${original_price}\n"
            f"Alternatives and their policy evaluations:\n{json.dumps(evaluations, indent=2)}\n\n"
            f"Provide your final policy assessment."
        )

        llm_response = await self._call_llm(POLICY_SYSTEM_PROMPT, user_message)
        task.tokens_used = 524
        task.cost_usd = 0.0004

        try:
            return json.loads(_sanitize_json(llm_response))  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            return {
                "policy_evaluation": evaluations,
                "auto_approve_eligible": any_auto_approve,
                "escalation_required": any_escalation,
                "policy_version": "v2.3",
            }

    def _get_mock_response(self, task: AgentTask) -> dict[str, Any]:
        task.tokens_used = 524
        task.cost_usd = 0.0004
        return {
            "policy_evaluation": [],
            "auto_approve_eligible": True,
            "escalation_required": False,
            "policy_version": "v2.3",
        }

    async def _call_llm(self, system_prompt: str, user_message: str) -> str:
        import boto3

        settings = get_settings()

        def _sync_call() -> str:
            client = boto3.client(
                "bedrock-runtime",
                region_name=settings.aws_region,
            )
            response = client.converse(
                modelId=self.model_id,
                system=[{"text": system_prompt}],
                messages=[{"role": "user", "content": [{"text": user_message}]}],
                inferenceConfig={"maxTokens": 2048, "temperature": 0.1},
            )
            return response["output"]["message"]["content"][0]["text"]  # type: ignore[no-any-return]

        return await asyncio.to_thread(_sync_call)

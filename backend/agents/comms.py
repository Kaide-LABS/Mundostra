"""Comms Agent — GPT-4o via OpenAI.

Drafts traveler-facing messages with empathy and clarity.
Optionally sends a real email if a GmailSender is configured.
"""

from __future__ import annotations

import json
from typing import Any

from backend.agents.base import BaseAgent
from backend.config import get_settings
from backend.logging_config import get_logger
from backend.models.tasks import AgentName, AgentTask, TraceStatus
from backend.orchestrator.prompts import COMMS_SYSTEM_PROMPT

logger = get_logger(__name__)


class CommsAgent(BaseAgent):
    agent_name = AgentName.COMMS

    def __init__(self, **kwargs: Any) -> None:
        self.gmail_sender = kwargs.pop("gmail_sender", None)
        super().__init__(**kwargs)
        settings = get_settings()
        self.model_id = settings.comms_model_id

    async def run(self, task: AgentTask) -> dict[str, Any]:
        event_data = task.input_data
        traveler = event_data.get("traveler", {})
        chosen = event_data.get("chosen_option", {})
        confidence = event_data.get("confidence_score", 0.0)

        await self.emit_trace(
            event_id=task.event_id,
            status=TraceStatus.WORKING,
            message=f"Drafting email notification for {traveler.get('name', 'traveler')}...",
        )

        if self.mock_llm:
            result = self._get_mock_response(task)
        else:
            user_message = (
                f"Traveler: {traveler.get('name', 'Unknown')}\n"
                f"Timezone: {traveler.get('timezone', 'America/Los_Angeles')}\n"
                f"Cancelled flight: {event_data.get('cancelled_flight', 'UA100')}\n"
                f"Route: {event_data.get('origin', 'SFO')} \u2192 {event_data.get('destination', 'JFK')}\n"
                f"Chosen replacement: {chosen.get('flight', 'UA105')}\n"
                f"Departure: {chosen.get('departure', '')}\n"
                f"Arrival: {chosen.get('arrival', '')}\n"
                f"Price: ${chosen.get('price', 0)}\n"
                f"Price change: {chosen.get('price_vs_original', '+$20')}\n"
                f"Calendar conflict: {chosen.get('calendar_conflict', False)}\n"
                f"Auto-approved: {event_data.get('auto_approved', True)}\n"
                f"Confidence score: {confidence}\n\n"
                f"Draft an email message for this traveler."
            )
            llm_response = await self._call_llm(COMMS_SYSTEM_PROMPT, user_message)
            task.tokens_used = 892
            task.cost_usd = 0.0045

            try:
                result = json.loads(llm_response)
            except json.JSONDecodeError:
                result = self._get_mock_response(task)

        # Send real email if sender is configured
        if self.gmail_sender is not None:
            result = await self._send_email(task, result, event_data, chosen, confidence)

        return result

    async def _send_email(
        self,
        task: AgentTask,
        result: dict[str, Any],
        event_data: dict[str, Any],
        chosen: dict[str, Any],
        confidence: float,
    ) -> dict[str, Any]:
        """Send an HTML email via Gmail and mark result as sent."""
        from backend.gmail.emails import build_resolution_email

        event_id_str = str(task.event_id)
        traveler = event_data.get("traveler", {})

        email = build_resolution_email(
            event_id=event_id_str,
            traveler_name=traveler.get("name", "Traveler"),
            cancelled_flight=event_data.get("cancelled_flight", ""),
            origin=event_data.get("origin", ""),
            destination=event_data.get("destination", ""),
            chosen_flight=chosen.get("flight", ""),
            departure=chosen.get("departure", ""),
            arrival=chosen.get("arrival", ""),
            price=float(chosen.get("price", 0)),
            price_delta=chosen.get("price_vs_original", ""),
            confidence=confidence,
            message_text=result.get("text", ""),
        )

        success = await self.gmail_sender.send_resolution(
            event_id=event_id_str,
            email=email,
        )

        result["email_sent"] = success

        await self.emit_trace(
            event_id=task.event_id,
            status=TraceStatus.WORKING,
            message=f"Email sent: {success}",
        )

        return result

    def _get_mock_response(self, task: AgentTask) -> dict[str, Any]:
        event_data = task.input_data
        traveler = event_data.get("traveler", {})
        chosen = event_data.get("chosen_option", {})
        name = traveler.get("name", "there")
        flight_num = chosen.get("flight", "UA105")
        cancelled = event_data.get("cancelled_flight", "UA100")
        origin = event_data.get("origin", "SFO")
        dest = event_data.get("destination", "JFK")
        price_delta = chosen.get("price_vs_original", "+$20")

        task.tokens_used = 892
        task.cost_usd = 0.0045

        return {
            "channel": "email",
            "text": (
                f"Hi {name} \u2014 your flight {cancelled} ({origin}\u2192{dest}) has been "
                f"cancelled. I've found you a seat on {flight_num}, departing at 6:30 PM "
                f"\u2014 gets you in by 11:45 PM, no conflict with your 10 AM meeting "
                f"tomorrow. The cost difference is {price_delta}, auto-approved under "
                f"company policy. Reply *confirm* to book, or *options* to see alternatives."
            ),
            "tone_score": "empathetic-professional",
            "urgency_flag": "high",
        }

    async def _call_llm(self, system_prompt: str, user_message: str) -> str:
        from openai import AsyncOpenAI

        settings = get_settings()
        client = AsyncOpenAI(api_key=settings.openai_api_key)

        response = await client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            response_format={"type": "json_object"},
            max_tokens=1024,
            temperature=0.7,
        )

        return response.choices[0].message.content or "{}"

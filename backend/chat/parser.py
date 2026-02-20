"""Chat message parser — mock (keyword) and LLM (Haiku) modes."""

from __future__ import annotations

import asyncio
import json
import re

from backend.config import get_settings
from backend.logging_config import get_logger
from backend.models.chat import ChatIntent, ChatParseResult

logger = get_logger(__name__)


class ChatParser:
    """Parse user chat messages into structured intents."""

    def __init__(self, *, mock_llm: bool = True) -> None:
        self.mock_llm = mock_llm

    async def parse(self, message: str) -> ChatParseResult:
        if self.mock_llm:
            return self._mock_parse(message)
        return await self._llm_parse(message)

    def _mock_parse(self, message: str) -> ChatParseResult:
        """Keyword-based parsing for mock/demo mode."""
        lower = message.lower().strip()

        # Check for flight disruption FIRST (contains "cancel" which overlaps with reject)
        if any(w in lower for w in ("cancelled", "delayed", "disrupted", "stranded", "flight")):
            flight_number = self._extract_flight_number(message)
            origin, destination = self._extract_airports(message)
            disruption = "cancelled" if "cancel" in lower else "delayed" if "delay" in lower else "cancelled"

            ack = "I'm sorry to hear about your flight disruption"
            if flight_number:
                ack = f"I'm sorry to hear your flight {flight_number} was {disruption}"
            ack += " — let me find alternatives for you right away."

            return ChatParseResult(
                intent=ChatIntent.FLIGHT_DISRUPTION,
                flight_number=flight_number,
                origin=origin,
                destination=destination,
                disruption_type=disruption,
                acknowledgment=ack,
            )

        # Select specific option: "book number 6", "option 3", "#2", "number 5"
        option_num = self._extract_option_number(lower)
        if option_num is not None:
            return ChatParseResult(
                intent=ChatIntent.CONFIRM,
                selected_option=option_num,
                acknowledgment=f"Got it — I'll book option {option_num} for you now.",
            )

        # Confirm (default recommendation)
        if any(w in lower for w in ("yes", "confirm", "book", "accept", "go ahead")):
            return ChatParseResult(
                intent=ChatIntent.CONFIRM,
                acknowledgment="Great, I'll confirm that booking for you now.",
            )

        # Options
        if any(w in lower for w in ("option", "other", "alternative", "show me", "what else")):
            return ChatParseResult(
                intent=ChatIntent.OPTIONS,
                acknowledgment="Of course — let me show you all available alternatives.",
            )

        # Reject
        if any(w in lower for w in ("no", "reject", "human", "agent", "speak")):
            return ChatParseResult(
                intent=ChatIntent.REJECT,
                acknowledgment="I understand. Let me connect you with a human agent.",
            )

        # Greeting
        if any(w in lower for w in ("hello", "hi", "hey", "good morning", "good afternoon")):
            return ChatParseResult(
                intent=ChatIntent.GREETING,
                acknowledgment="Hello! I'm your Mundostra travel assistant. How can I help you today?",
            )

        return ChatParseResult(
            intent=ChatIntent.UNKNOWN,
            acknowledgment="I'm not sure I understood that. Could you tell me about your travel issue?",
        )

    def _extract_option_number(self, lower: str) -> int | None:
        """Extract option number from messages like 'book number 6', 'option 3', '#2'."""
        patterns = [
            r"(?:book|choose|select|pick|want|go with|take)\s+(?:number|option|#|no\.?)\s*(\d+)",
            r"(?:number|option|#|no\.?)\s*(\d+)",
            r"(?:book|choose|select|pick|want|go with|take)\s+(\d+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, lower)
            if match:
                num = int(match.group(1))
                if 1 <= num <= 20:  # sanity bound
                    return num
        return None

    def _extract_flight_number(self, message: str) -> str | None:
        """Extract flight number like 'UA 2381' or 'UA2381'."""
        match = re.search(r"\b([A-Z]{2})\s*(\d{1,5})\b", message, re.IGNORECASE)
        if match:
            return f"{match.group(1).upper()} {match.group(2)}"
        return None

    def _extract_airports(self, message: str) -> tuple[str | None, str | None]:
        """Extract airport codes like 'SFO' 'JFK'."""
        codes = re.findall(r"\b([A-Z]{3})\b", message)
        origin = codes[0] if len(codes) >= 1 else None
        destination = codes[1] if len(codes) >= 2 else None
        return origin, destination

    async def _llm_parse(self, message: str) -> ChatParseResult:
        """Use Claude 3.5 Haiku via Bedrock for intent parsing."""
        from backend.chat.prompts import CHAT_PARSER_SYSTEM_PROMPT

        settings = get_settings()

        def _sync_call() -> str:
            import boto3

            client = boto3.client(
                "bedrock-runtime",
                region_name=settings.aws_region,
            )
            response = client.converse(
                modelId=settings.policy_model_id,  # Haiku — fast and cheap
                system=[{"text": CHAT_PARSER_SYSTEM_PROMPT}],
                messages=[{"role": "user", "content": [{"text": message}]}],
                inferenceConfig={"maxTokens": 512, "temperature": 0.1},
            )
            return response["output"]["message"]["content"][0]["text"]  # type: ignore[no-any-return]

        try:
            raw = await asyncio.to_thread(_sync_call)
            data = json.loads(raw.strip())
            return ChatParseResult(
                intent=ChatIntent(data.get("intent", "unknown")),
                flight_number=data.get("flight_number"),
                origin=data.get("origin"),
                destination=data.get("destination"),
                disruption_type=data.get("disruption_type"),
                selected_option=data.get("selected_option"),
                acknowledgment=data.get("acknowledgment", ""),
            )
        except Exception as exc:
            await logger.awarning("chat_parse_llm_failed", error=str(exc))
            return self._mock_parse(message)

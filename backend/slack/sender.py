"""SlackSender — sends and updates Block Kit messages via the Slack SDK."""

from __future__ import annotations

from typing import Any

from backend.logging_config import get_logger

logger = get_logger(__name__)


class SlackSender:
    """Thin wrapper around the Slack WebClient for sending resolution messages.

    Stores a mapping of event_id -> (channel, ts) so messages can be updated
    when the traveler responds.
    """

    def __init__(self, bot_token: str, default_channel: str) -> None:
        from slack_sdk.web.async_client import AsyncWebClient

        self.client = AsyncWebClient(token=bot_token)
        self.default_channel = default_channel
        self._message_map: dict[str, tuple[str, str]] = {}  # event_id -> (channel, ts)

    async def send_resolution(
        self,
        *,
        event_id: str,
        channel: str | None = None,
        text: str,
        blocks: list[dict[str, Any]],
    ) -> tuple[str, str]:
        """Post a Block Kit message and store the ts for later updates.

        Returns (channel, ts).
        """
        target_channel = channel or self.default_channel
        response = await self.client.chat_postMessage(
            channel=target_channel,
            text=text,
            blocks=blocks,
        )
        ts = response["ts"]
        self._message_map[event_id] = (target_channel, ts)
        await logger.ainfo(
            "slack_message_sent",
            event_id=event_id,
            channel=target_channel,
            ts=ts,
        )
        return (target_channel, ts)

    async def update_message(
        self,
        *,
        event_id: str,
        blocks: list[dict[str, Any]],
        text: str = "",
    ) -> None:
        """Update a previously sent message (e.g. after confirm/options)."""
        mapping = self._message_map.get(event_id)
        if not mapping:
            await logger.awarning("slack_update_no_mapping", event_id=event_id)
            return
        channel, ts = mapping
        await self.client.chat_update(
            channel=channel,
            ts=ts,
            text=text or "Updated",
            blocks=blocks,
        )

    def get_message_info(self, event_id: str) -> tuple[str, str] | None:
        """Return (channel, ts) for an event, or None."""
        return self._message_map.get(event_id)

    def clear_mappings(self) -> None:
        """Clear all stored message mappings (used on demo reset)."""
        self._message_map.clear()

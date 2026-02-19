"""TeamsSender — posts Adaptive Cards to a Microsoft Teams Incoming Webhook."""

from __future__ import annotations

from typing import Any

import httpx

from backend.logging_config import get_logger

logger = get_logger(__name__)


class TeamsSender:
    """Posts Adaptive Cards to Teams via an Incoming Webhook URL.

    Unlike Slack, Teams webhooks are fire-and-forget (returns ``1`` on success,
    not JSON) and do not support message updates, so there is no message map.
    """

    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def send_resolution(
        self,
        *,
        event_id: str,
        card: dict[str, Any],
    ) -> bool:
        """POST the Adaptive Card JSON to the webhook.

        Returns True on success, False otherwise.
        """
        async with httpx.AsyncClient() as client:
            resp = await client.post(self.webhook_url, json=card, timeout=10.0)

        # Teams returns the string "1" on success
        success = resp.status_code == 200
        await logger.ainfo(
            "teams_message_sent",
            event_id=event_id,
            success=success,
            status_code=resp.status_code,
        )
        return success

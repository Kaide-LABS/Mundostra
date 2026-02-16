"""Slack Bolt async app — handles interactive button presses from Slack."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from backend.logging_config import get_logger

if TYPE_CHECKING:
    from backend.orchestrator.engine import OrchestratorEngine

logger = get_logger(__name__)


def create_slack_app(
    *,
    signing_secret: str,
    bot_token: str,
    engine_getter: Any,
) -> Any:
    """Create and configure a Slack Bolt AsyncApp.

    engine_getter is a callable returning the OrchestratorEngine (deferred to
    avoid circular imports and to pick up the runtime-initialized engine).
    """
    from slack_bolt.async_app import AsyncApp

    slack_app = AsyncApp(
        signing_secret=signing_secret,
        token=bot_token,
    )

    @slack_app.action("traveler_confirm")
    async def handle_confirm(ack: Any, body: Any, respond: Any) -> None:
        await ack()
        event_id = body["actions"][0]["value"]
        engine: OrchestratorEngine = engine_getter()

        await logger.ainfo("slack_confirm_received", event_id=event_id)

        from backend.models.responses import TravelerResponse, TravelerResponseType

        response = TravelerResponse(
            event_id=event_id,
            response_type=TravelerResponseType.CONFIRM,
        )
        await engine.respond_to_event(event_id, response)

    @slack_app.action("traveler_options")
    async def handle_options(ack: Any, body: Any, respond: Any) -> None:
        await ack()
        event_id = body["actions"][0]["value"]
        engine: OrchestratorEngine = engine_getter()

        await logger.ainfo("slack_options_received", event_id=event_id)

        from backend.models.responses import TravelerResponse, TravelerResponseType

        response = TravelerResponse(
            event_id=event_id,
            response_type=TravelerResponseType.OPTIONS,
        )
        await engine.respond_to_event(event_id, response)

    return slack_app

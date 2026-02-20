"""Shared test fixtures."""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient

# Force mock LLM mode for all tests
os.environ["MOCK_LLM"] = "true"
os.environ["APP_ENV"] = "test"
os.environ["BASE_URL"] = "http://test"

import backend.main as main_module  # noqa: E402
from backend.chat.parser import ChatParser  # noqa: E402
from backend.main import _init_engine, app, bus  # noqa: E402
from backend.models.events import (  # noqa: E402
    EventType,
    FlightDetails,
    PolicyTier,
    TravelerProfile,
    TravelEvent,
)

# Create the ASGI transport and initialize the engine with it
_transport = ASGITransport(app=app)  # type: ignore[arg-type]
_init_engine(http_transport=_transport)

# Initialize chat parser for tests
main_module.chat_parser = ChatParser(mock_llm=True)


@pytest.fixture
def sample_event() -> TravelEvent:
    """The PRD's primary scenario: Sarah Chen's flight cancellation."""
    return TravelEvent(
        event_type=EventType.FLIGHT_CANCELLED,
        booking_ref="MND-2025-00847",
        flight=FlightDetails(
            number="UA100",
            origin="SFO",
            destination="JFK",
            scheduled_departure=datetime.now().replace(hour=16, minute=0, second=0, microsecond=0),
            status="cancelled",
            reason="mechanical",
            original_price=400.0,
        ),
        traveler=TravelerProfile(
            name="Sarah Chen",
            email="sarah@designpartner.com",
            role="VP Engineering",
            policy_tier=PolicyTier.EXECUTIVE,
            messaging_id="U0123SARAH",
            timezone="America/Los_Angeles",
            calendar_integration=True,
        ),
    )


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    """Async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(transport=_transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture(autouse=True)
def _clean_state() -> None:
    """Clean state between tests."""
    main_module.engine.resolutions.clear()
    bus._history.clear()
    main_module.chat_sessions.clear()
    main_module.chat_pending.clear()
    main_module.chat_events.clear()

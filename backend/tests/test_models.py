"""Tests for Pydantic data models."""

from __future__ import annotations

from datetime import datetime

from backend.models.events import (
    EventType,
    FlightDetails,
    PolicyTier,
    TravelerProfile,
    TravelEvent,
)
from backend.models.resolutions import (
    FlightAlternative,
    Resolution,
    ResolutionStatus,
)
from backend.models.tasks import (
    AgentName,
    AgentTask,
    AgentTraceEntry,
    TaskStatus,
    TraceStatus,
)


class TestEventModels:
    def test_event_type_enum(self) -> None:
        assert EventType.FLIGHT_CANCELLED == "flight_cancelled"
        assert EventType.FLIGHT_DELAYED == "flight_delayed"

    def test_policy_tier_enum(self) -> None:
        assert PolicyTier.EXECUTIVE == "executive"
        assert PolicyTier.STANDARD == "standard"
        assert PolicyTier.MANAGER == "manager"

    def test_flight_details(self) -> None:
        flight = FlightDetails(
            number="UA100",
            origin="SFO",
            destination="JFK",
            scheduled_departure=datetime(2025, 2, 12, 16, 0, 0),
            status="cancelled",
            reason="mechanical",
        )
        assert flight.number == "UA100"
        assert flight.original_price == 400.0

    def test_traveler_profile_defaults(self) -> None:
        traveler = TravelerProfile(
            name="Sarah Chen",
            email="sarah@test.com",
            role="VP Engineering",
            policy_tier=PolicyTier.EXECUTIVE,
            slack_id="U123",
        )
        assert traveler.timezone == "America/Los_Angeles"
        assert traveler.calendar_integration is True
        assert traveler.id is not None

    def test_travel_event_serialization(self) -> None:
        event = TravelEvent(
            event_type=EventType.FLIGHT_CANCELLED,
            booking_ref="MND-001",
            traveler=TravelerProfile(
                name="Test User",
                email="test@test.com",
                role="IC",
                policy_tier=PolicyTier.STANDARD,
                slack_id="U999",
            ),
        )
        data = event.model_dump(mode="json")
        assert data["event_type"] == "flight_cancelled"
        assert data["booking_ref"] == "MND-001"
        assert "id" in data

    def test_travel_event_uuid_auto_generated(self) -> None:
        e1 = TravelEvent(
            event_type=EventType.FLIGHT_CANCELLED,
            booking_ref="A",
            traveler=TravelerProfile(
                name="A",
                email="a@a.com",
                role="A",
                policy_tier=PolicyTier.STANDARD,
                slack_id="A",
            ),
        )
        e2 = TravelEvent(
            event_type=EventType.FLIGHT_CANCELLED,
            booking_ref="B",
            traveler=TravelerProfile(
                name="B",
                email="b@b.com",
                role="B",
                policy_tier=PolicyTier.STANDARD,
                slack_id="B",
            ),
        )
        assert e1.id != e2.id


class TestTaskModels:
    def test_agent_name_enum(self) -> None:
        assert AgentName.ORCHESTRATOR == "orchestrator"
        assert AgentName.RESEARCH == "research"
        assert AgentName.POLICY == "policy"
        assert AgentName.COMMS == "comms"

    def test_task_status_enum(self) -> None:
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.RUNNING == "running"
        assert TaskStatus.COMPLETE == "complete"
        assert TaskStatus.FAILED == "failed"

    def test_agent_task_defaults(self) -> None:
        from uuid import uuid4

        task = AgentTask(event_id=uuid4(), agent=AgentName.RESEARCH)
        assert task.status == TaskStatus.PENDING
        assert task.tokens_used == 0
        assert task.output_data is None

    def test_trace_entry_serialization(self) -> None:
        from uuid import uuid4

        entry = AgentTraceEntry(
            event_id=uuid4(),
            agent=AgentName.RESEARCH,
            model="gemini-2.0-flash",
            status=TraceStatus.WORKING,
            message="Searching flights...",
        )
        data = entry.model_dump(mode="json")
        assert data["agent"] == "research"
        assert data["status"] == "working"


class TestResolutionModels:
    def test_flight_alternative(self) -> None:
        alt = FlightAlternative(
            flight="UA105",
            departure=datetime(2025, 2, 12, 18, 30),
            arrival=datetime(2025, 2, 12, 23, 45),
            price=420.0,
        )
        assert alt.calendar_conflict is False
        assert alt.seat_available is True
        assert alt.source == "mock_inventory_api"

    def test_resolution_defaults(self) -> None:
        from uuid import uuid4

        res = Resolution(event_id=uuid4())
        assert res.status == ResolutionStatus.PROPOSED
        assert res.confidence_score == 0.0
        assert res.chosen_option is None

    def test_resolution_serialization(self) -> None:
        from uuid import uuid4

        res = Resolution(
            event_id=uuid4(),
            status=ResolutionStatus.ESCALATED,
            confidence_score=0.3,
        )
        data = res.model_dump(mode="json")
        assert data["status"] == "escalated"
        assert data["confidence_score"] == 0.3

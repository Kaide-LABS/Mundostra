"""Tests for the orchestrator engine."""

from __future__ import annotations

import pytest

from backend.message_bus.bus import MessageBus
from backend.models.events import TravelEvent
from backend.orchestrator.engine import OrchestratorEngine


@pytest.fixture
def orch_bus() -> MessageBus:
    return MessageBus()


class TestOrchestratorSynthesis:
    def test_mock_synthesis_picks_cheapest_compliant(self, orch_bus: MessageBus) -> None:
        engine = OrchestratorEngine(orch_bus)

        research_output = {
            "alternatives": [
                {
                    "flight": "UA105",
                    "price": 420.0,
                    "calendar_conflict": False,
                    "seat_available": True,
                },
                {
                    "flight": "AA210",
                    "price": 385.0,
                    "calendar_conflict": False,
                    "seat_available": True,
                },
                {
                    "flight": "UA900",
                    "price": 310.0,
                    "calendar_conflict": True,
                    "seat_available": True,
                },
            ],
        }
        policy_output = {
            "policy_evaluation": [
                {"flight": "UA105", "price": 420.0, "compliant": True, "approval_required": False},
                {"flight": "AA210", "price": 385.0, "compliant": True, "approval_required": False},
                {"flight": "UA900", "price": 310.0, "compliant": True, "approval_required": False},
            ],
        }

        result = engine._mock_synthesis(research_output, policy_output)
        # AA210 is cheapest no-conflict compliant option
        assert result["chosen_flight"] == "AA210"
        assert result["confidence_score"] == 0.94
        assert result["policy_compliant"] is True

    def test_mock_synthesis_escalates_when_no_viable(self, orch_bus: MessageBus) -> None:
        engine = OrchestratorEngine(orch_bus)

        research_output = {
            "alternatives": [
                {"flight": "X1", "price": 999, "calendar_conflict": True, "seat_available": True},
            ],
        }
        policy_output = {
            "policy_evaluation": [
                {"flight": "X1", "price": 999, "compliant": False, "approval_required": True},
            ],
        }

        result = engine._mock_synthesis(research_output, policy_output)
        # Falls back: only non-conflict options
        # X1 has conflict → no viable → escalation
        assert result["confidence_score"] < 0.7
        assert result["escalation_needed"] is True

    def test_get_resolution_returns_none_for_unknown(self, orch_bus: MessageBus) -> None:
        from uuid import uuid4

        engine = OrchestratorEngine(orch_bus)
        assert engine.get_resolution(uuid4()) is None


class TestOrchestratorE2EMock:
    @pytest.mark.asyncio
    async def test_handle_event_produces_resolution(
        self, sample_event: TravelEvent, client: object
    ) -> None:
        """Full orchestrator run with mock LLM — the primary success criterion."""
        from httpx import AsyncClient

        http_client: AsyncClient = client  # type: ignore[assignment]

        resp = await http_client.post(
            "/api/events",
            json=sample_event.model_dump(mode="json"),
        )
        assert resp.status_code == 200
        data = resp.json()

        assert "event_id" in data
        assert "confidence_score" in data
        assert data["confidence_score"] > 0
        assert data["status"] in ["proposed", "escalated"]
        assert len(data["agents_involved"]) >= 3

    @pytest.mark.asyncio
    async def test_trace_populated_after_event(
        self, sample_event: TravelEvent, client: object
    ) -> None:
        from httpx import AsyncClient

        http_client: AsyncClient = client  # type: ignore[assignment]

        resp = await http_client.post(
            "/api/events",
            json=sample_event.model_dump(mode="json"),
        )
        event_id = resp.json()["event_id"]

        trace_resp = await http_client.get(f"/api/events/{event_id}/trace")
        assert trace_resp.status_code == 200
        trace_data = trace_resp.json()
        assert trace_data["trace_count"] > 0
        assert len(trace_data["trace"]) > 0

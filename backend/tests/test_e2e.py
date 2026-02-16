"""End-to-end test: the PRD's primary success criterion.

Trigger event → all agents run → resolution produced.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from backend.models.events import TravelEvent


class TestEndToEnd:
    @pytest.mark.asyncio
    async def test_full_flight_cancellation_resolution(
        self, sample_event: TravelEvent, client: AsyncClient
    ) -> None:
        """The Sarah Chen scenario: flight cancelled → agents coordinate → resolution."""
        # 1. Trigger the event
        resp = await client.post(
            "/api/events",
            json=sample_event.model_dump(mode="json"),
        )
        assert resp.status_code == 200
        resolution = resp.json()

        # 2. Verify resolution structure
        assert resolution["status"] == "proposed"
        assert resolution["confidence_score"] >= 0.7
        assert resolution["policy_compliant"] is True

        # 3. Verify chosen option exists
        assert resolution["chosen_option"] is not None
        chosen = resolution["chosen_option"]
        assert "flight" in chosen
        assert "price" in chosen
        assert chosen["calendar_conflict"] is False

        # 4. Verify all agents were involved
        agents = resolution["agents_involved"]
        assert "orchestrator" in agents
        assert "research" in agents
        assert "policy" in agents
        assert "comms" in agents

        # 5. Verify comms result exists
        assert resolution["comms_result"] is not None
        assert resolution["comms_result"]["channel"] == "slack"
        assert len(resolution["comms_result"]["text"]) > 0

        # 6. Verify research result
        assert resolution["research_result"] is not None
        assert len(resolution["research_result"]["alternatives"]) > 0

        # 7. Verify policy result
        assert resolution["policy_result"] is not None

        # 8. Verify timing and cost
        assert resolution["total_time_seconds"] > 0
        assert resolution["total_cost_usd"] > 0

    @pytest.mark.asyncio
    async def test_event_retrieval_after_resolution(
        self, sample_event: TravelEvent, client: AsyncClient
    ) -> None:
        """After triggering, we can retrieve the resolution by event ID."""
        resp = await client.post(
            "/api/events",
            json=sample_event.model_dump(mode="json"),
        )
        event_id = resp.json()["event_id"]

        # Retrieve
        get_resp = await client.get(f"/api/events/{event_id}")
        assert get_resp.status_code == 200
        data = get_resp.json()
        assert data["event_id"] == event_id

    @pytest.mark.asyncio
    async def test_trace_has_all_agent_entries(
        self, sample_event: TravelEvent, client: AsyncClient
    ) -> None:
        """The trace should contain entries from all agents."""
        resp = await client.post(
            "/api/events",
            json=sample_event.model_dump(mode="json"),
        )
        event_id = resp.json()["event_id"]

        trace_resp = await client.get(f"/api/events/{event_id}/trace")
        trace = trace_resp.json()["trace"]

        agents_in_trace = {entry["agent"] for entry in trace}
        assert "orchestrator" in agents_in_trace
        assert "research" in agents_in_trace
        assert "policy" in agents_in_trace
        assert "comms" in agents_in_trace

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient) -> None:
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "ok"

    @pytest.mark.asyncio
    async def test_unknown_event_returns_error(self, client: AsyncClient) -> None:
        from uuid import uuid4

        resp = await client.get(f"/api/events/{uuid4()}")
        assert resp.status_code == 200
        data = resp.json()
        assert "error" in data

"""Tests for POST /api/events/{event_id}/respond endpoint."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from backend.models.events import TravelEvent


@pytest.mark.asyncio
async def test_confirm_response(client: AsyncClient, sample_event: TravelEvent) -> None:
    """Confirm response sets status to confirmed and triggers card authorization trace."""
    # Trigger event first
    resp = await client.post("/api/events", content=sample_event.model_dump_json())
    assert resp.status_code == 200
    resolution = resp.json()
    event_id = resolution["event_id"]

    # Confirm the resolution
    resp = await client.post(
        f"/api/events/{event_id}/respond",
        json={"event_id": event_id, "response_type": "confirm"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "confirmed"

    # Check trace has card authorization entries
    trace_resp = await client.get(f"/api/events/{event_id}/trace")
    trace = trace_resp.json()["trace"]
    messages = [e["message"] for e in trace]
    assert any("card" in m.lower() or "authorized" in m.lower() for m in messages)


@pytest.mark.asyncio
async def test_options_response(client: AsyncClient, sample_event: TravelEvent) -> None:
    """Options response keeps status as proposed and emits alternatives trace."""
    resp = await client.post("/api/events", content=sample_event.model_dump_json())
    resolution = resp.json()
    event_id = resolution["event_id"]

    resp = await client.post(
        f"/api/events/{event_id}/respond",
        json={"event_id": event_id, "response_type": "options"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # Options keeps it as proposed
    assert data["status"] == "proposed"


@pytest.mark.asyncio
async def test_reject_response(client: AsyncClient, sample_event: TravelEvent) -> None:
    """Reject response sets status to rejected."""
    resp = await client.post("/api/events", content=sample_event.model_dump_json())
    resolution = resp.json()
    event_id = resolution["event_id"]

    resp = await client.post(
        f"/api/events/{event_id}/respond",
        json={"event_id": event_id, "response_type": "reject"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "rejected"


@pytest.mark.asyncio
async def test_respond_nonexistent_event(client: AsyncClient) -> None:
    """Responding to nonexistent event returns error."""
    fake_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.post(
        f"/api/events/{fake_id}/respond",
        json={"event_id": fake_id, "response_type": "confirm"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "error" in data

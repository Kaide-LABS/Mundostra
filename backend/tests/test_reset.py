"""Tests for POST /api/reset endpoint."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from backend.models.events import TravelEvent


@pytest.mark.asyncio
async def test_reset_clears_resolutions(client: AsyncClient, sample_event: TravelEvent) -> None:
    """Reset clears all stored resolutions."""
    # Create a resolution
    resp = await client.post("/api/events", content=sample_event.model_dump_json())
    assert resp.status_code == 200
    event_id = resp.json()["event_id"]

    # Verify it exists
    resp = await client.get(f"/api/events/{event_id}")
    assert resp.status_code == 200
    assert "error" not in resp.json()

    # Reset
    resp = await client.post("/api/reset")
    assert resp.status_code == 200
    assert resp.json()["status"] == "reset"

    # Verify it's gone
    resp = await client.get(f"/api/events/{event_id}")
    data = resp.json()
    assert "error" in data


@pytest.mark.asyncio
async def test_reset_clears_trace(client: AsyncClient, sample_event: TravelEvent) -> None:
    """Reset clears trace history."""
    resp = await client.post("/api/events", content=sample_event.model_dump_json())
    event_id = resp.json()["event_id"]

    # Verify trace exists
    resp = await client.get(f"/api/events/{event_id}/trace")
    assert resp.json()["trace_count"] > 0

    # Reset
    await client.post("/api/reset")

    # Trace should be empty now
    resp = await client.get(f"/api/events/{event_id}/trace")
    assert resp.json()["trace_count"] == 0


@pytest.mark.asyncio
async def test_reset_returns_success(client: AsyncClient) -> None:
    """Reset returns success even with no data to clear."""
    resp = await client.post("/api/reset")
    assert resp.status_code == 200
    assert resp.json() == {"status": "reset"}

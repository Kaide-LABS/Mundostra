"""Tests for mock API endpoints."""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest
from httpx import AsyncClient


class TestFlightsMockAPI:
    @pytest.mark.asyncio
    async def test_search_returns_alternatives(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/mock/flights/search", params={"origin": "SFO", "destination": "JFK"}
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["origin"] == "SFO"
        assert data["destination"] == "JFK"
        assert data["results_count"] == 7
        assert len(data["alternatives"]) == 7

    @pytest.mark.asyncio
    async def test_alternatives_have_required_fields(self, client: AsyncClient) -> None:
        resp = await client.get("/mock/flights/search")
        data = resp.json()
        alt = data["alternatives"][0]
        assert "flight" in alt
        assert "price" in alt
        assert "departure" in alt
        assert "arrival" in alt
        assert "seat_available" in alt

    @pytest.mark.asyncio
    async def test_includes_unavailable_and_expensive(self, client: AsyncClient) -> None:
        resp = await client.get("/mock/flights/search")
        alts = resp.json()["alternatives"]
        prices = [a["price"] for a in alts]
        assert max(prices) == 680.0  # Business class
        assert any(not a["seat_available"] for a in alts)  # DL800


class TestCalendarMockAPI:
    @pytest.mark.asyncio
    async def test_no_conflict_for_evening_arrival(self, client: AsyncClient) -> None:
        today = date.today()
        arrival = datetime(today.year, today.month, today.day, 23, 45, 0)
        resp = await client.get(
            "/mock/calendar/check",
            params={"arrival_time": arrival.isoformat()},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["has_conflict"] is False

    @pytest.mark.asyncio
    async def test_conflict_for_late_arrival(self, client: AsyncClient) -> None:
        tomorrow = date.today() + timedelta(days=1)
        arrival = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 9, 0, 0)
        resp = await client.get(
            "/mock/calendar/check",
            params={"arrival_time": arrival.isoformat()},
        )
        data = resp.json()
        assert data["has_conflict"] is True
        assert "Board Meeting" in data["conflict_details"]

    @pytest.mark.asyncio
    async def test_returns_meetings(self, client: AsyncClient) -> None:
        resp = await client.get("/mock/calendar/check")
        data = resp.json()
        assert len(data["meetings"]) == 2
        assert data["next_critical_meeting"]["title"] == "Board Meeting"


class TestPolicyMockAPI:
    @pytest.mark.asyncio
    async def test_executive_within_cap(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/mock/policy/evaluate",
            params={
                "policy_tier": "executive",
                "original_price": 400,
                "proposed_price": 420,
            },
        )
        data = resp.json()
        assert data["within_cap"] is True
        assert data["auto_approve_eligible"] is True
        assert data["budget_status"] == "within_cap"

    @pytest.mark.asyncio
    async def test_standard_exceeds_cap(self, client: AsyncClient) -> None:
        resp = await client.get(
            "/mock/policy/evaluate",
            params={
                "policy_tier": "standard",
                "original_price": 400,
                "proposed_price": 680,
            },
        )
        data = resp.json()
        assert data["within_cap"] is False
        assert data["escalation_required"] is True

    @pytest.mark.asyncio
    async def test_auto_approve_threshold(self, client: AsyncClient) -> None:
        # Standard tier: auto-approve delta is $25
        resp = await client.get(
            "/mock/policy/evaluate",
            params={
                "policy_tier": "standard",
                "original_price": 400,
                "proposed_price": 430,
            },
        )
        data = resp.json()
        # $30 delta > $25 threshold → not auto-approvable
        assert data["auto_approve_eligible"] is False


class TestCardsMockAPI:
    @pytest.mark.asyncio
    async def test_authorization_succeeds(self, client: AsyncClient) -> None:
        resp = await client.post(
            "/mock/cards/authorize",
            json={"booking_ref": "MND-001", "amount": 420.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "approved"
        assert "authorization_id" in data
        assert data["amount"] == 420.0

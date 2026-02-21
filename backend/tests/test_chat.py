"""Tests for chat interface — parser + endpoints."""

from __future__ import annotations

import asyncio

import pytest
from httpx import AsyncClient

from backend.chat.parser import ChatParser
from backend.models.chat import ChatIntent


class TestChatParser:
    """Unit tests for the mock keyword parser."""

    @pytest.fixture
    def parser(self) -> ChatParser:
        return ChatParser(mock_llm=True)

    @pytest.mark.asyncio
    async def test_parse_flight_cancellation(self, parser: ChatParser) -> None:
        result = await parser.parse("My flight UA 2381 from SFO to JFK got cancelled")
        assert result.intent == ChatIntent.FLIGHT_DISRUPTION
        assert result.flight_number == "UA 2381"
        assert result.origin == "SFO"
        assert result.destination == "JFK"
        assert result.disruption_type == "cancelled"

    @pytest.mark.asyncio
    async def test_parse_flight_delay(self, parser: ChatParser) -> None:
        result = await parser.parse("My flight AA 100 is delayed")
        assert result.intent == ChatIntent.FLIGHT_DISRUPTION
        assert result.flight_number == "AA 100"
        assert result.disruption_type == "delayed"

    @pytest.mark.asyncio
    async def test_parse_generic_flight(self, parser: ChatParser) -> None:
        result = await parser.parse("my flight got cancelled")
        assert result.intent == ChatIntent.FLIGHT_DISRUPTION
        assert result.flight_number is None

    @pytest.mark.asyncio
    async def test_parse_confirm(self, parser: ChatParser) -> None:
        result = await parser.parse("Yes, book that one")
        assert result.intent == ChatIntent.CONFIRM

    @pytest.mark.asyncio
    async def test_parse_options(self, parser: ChatParser) -> None:
        result = await parser.parse("Show me other options")
        assert result.intent == ChatIntent.OPTIONS

    @pytest.mark.asyncio
    async def test_parse_reject(self, parser: ChatParser) -> None:
        result = await parser.parse("No, I want to speak to a human agent")
        assert result.intent == ChatIntent.REJECT

    @pytest.mark.asyncio
    async def test_parse_greeting(self, parser: ChatParser) -> None:
        result = await parser.parse("Hello")
        assert result.intent == ChatIntent.GREETING

    @pytest.mark.asyncio
    async def test_parse_unknown(self, parser: ChatParser) -> None:
        result = await parser.parse("what is the weather today")
        assert result.intent == ChatIntent.UNKNOWN


class TestChatEndpoints:
    """Integration tests for chat API endpoints."""

    @pytest.mark.asyncio
    async def test_chat_greeting(self, client: AsyncClient) -> None:
        resp = await client.post("/api/chat", json={"message": "Hello"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "greeting"
        assert "session_id" in data

    @pytest.mark.asyncio
    async def test_chat_flight_disruption_with_all_details(self, client: AsyncClient) -> None:
        """Full details provided → orchestration fires immediately."""
        resp = await client.post(
            "/api/chat",
            json={
                "message": "My flight UA 2381 from SFO to JFK got cancelled",
                "session_id": "full-details",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "flight_disruption"
        assert data["status"] == "processing"
        assert "event_id" in data
        assert data["session_id"] == "full-details"

    @pytest.mark.asyncio
    async def test_chat_flight_no_details_enters_gathering(self, client: AsyncClient) -> None:
        """No details → gathering mode asks for flight number."""
        resp = await client.post(
            "/api/chat",
            json={"message": "My flight got cancelled", "session_id": "gather-1"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "flight_disruption"
        assert data["status"] == "gathering"
        assert "flight number" in data["acknowledgment"].lower()

    @pytest.mark.asyncio
    async def test_chat_partial_details_asks_missing(self, client: AsyncClient) -> None:
        """Flight + origin provided, no destination → asks for destination."""
        resp = await client.post(
            "/api/chat",
            json={
                "message": "My flight UA 100 from SFO got cancelled",
                "session_id": "partial-1",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "gathering"
        assert "flying to" in data["acknowledgment"].lower()

    @pytest.mark.asyncio
    async def test_chat_gathering_full_flow(self, client: AsyncClient) -> None:
        """Multi-turn: no details → flight → origin → destination → orchestration."""
        sid = "gather-full"

        # Step 1: report disruption with no details
        r1 = await client.post(
            "/api/chat", json={"message": "my flight got cancelled", "session_id": sid}
        )
        d1 = r1.json()
        assert d1["status"] == "gathering"
        assert "flight number" in d1["acknowledgment"].lower()

        # Step 2: provide flight number
        r2 = await client.post(
            "/api/chat", json={"message": "UA 100", "session_id": sid}
        )
        d2 = r2.json()
        assert d2["status"] == "gathering"
        assert d2["intent"] == "info_response"
        assert "departing" in d2["acknowledgment"].lower() or "airport" in d2["acknowledgment"].lower()

        # Step 3: provide origin
        r3 = await client.post(
            "/api/chat", json={"message": "SFO", "session_id": sid}
        )
        d3 = r3.json()
        assert d3["status"] == "gathering"
        assert "flying to" in d3["acknowledgment"].lower()

        # Step 4: provide destination → triggers orchestration
        r4 = await client.post(
            "/api/chat", json={"message": "JFK", "session_id": sid}
        )
        d4 = r4.json()
        assert d4["status"] == "processing"
        assert "event_id" in d4

    @pytest.mark.asyncio
    async def test_chat_poll_until_complete(self, client: AsyncClient) -> None:
        # Trigger disruption with full details
        resp = await client.post(
            "/api/chat",
            json={
                "message": "My flight UA 2381 from SFO to JFK got cancelled",
                "session_id": "poll-test",
            },
        )
        data = resp.json()
        event_id = data["event_id"]

        for _ in range(120):
            await asyncio.sleep(0.1)
            status_resp = await client.get(f"/api/chat/status/{event_id}")
            status_data = status_resp.json()
            if status_data["status"] == "complete":
                assert "resolution" in status_data
                resolution = status_data["resolution"]
                assert resolution["status"] == "proposed"
                assert resolution["confidence_score"] >= 0.7
                return

        pytest.fail("Resolution did not complete within polling window")

    @pytest.mark.asyncio
    async def test_chat_confirm_after_resolution(self, client: AsyncClient) -> None:
        # Trigger disruption with full details
        resp = await client.post(
            "/api/chat",
            json={
                "message": "My flight UA 2381 from SFO to JFK got cancelled",
                "session_id": "confirm-test",
            },
        )
        data = resp.json()
        event_id = data["event_id"]

        # Wait for resolution
        for _ in range(120):
            await asyncio.sleep(0.1)
            status_resp = await client.get(f"/api/chat/status/{event_id}")
            if status_resp.json()["status"] == "complete":
                break

        # Send confirm
        confirm_resp = await client.post(
            "/api/chat",
            json={"message": "Yes, book it", "session_id": "confirm-test"},
        )
        confirm_data = confirm_resp.json()
        assert confirm_data["intent"] == "confirm"
        assert confirm_data["status"] == "complete"
        assert confirm_data["resolution"]["status"] == "confirmed"

    @pytest.mark.asyncio
    async def test_chat_status_not_found(self, client: AsyncClient) -> None:
        resp = await client.get("/api/chat/status/nonexistent-id")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "processing"

    @pytest.mark.asyncio
    async def test_chat_unknown_intent(self, client: AsyncClient) -> None:
        resp = await client.post("/api/chat", json={"message": "what is the weather"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "unknown"

    @pytest.mark.asyncio
    async def test_reset_clears_chat_state(self, client: AsyncClient) -> None:
        # Trigger a chat event with full details
        await client.post(
            "/api/chat",
            json={
                "message": "My flight UA 2381 from SFO to JFK got cancelled",
                "session_id": "reset-test",
            },
        )

        # Reset
        resp = await client.post("/api/reset")
        assert resp.status_code == 200

        # Verify no active session
        resp = await client.post(
            "/api/chat",
            json={"message": "Yes confirm", "session_id": "reset-test"},
        )
        data = resp.json()
        assert data.get("status") == "no_active_event"

    @pytest.mark.asyncio
    async def test_chat_image_upload_triggers_ocr(self, client: AsyncClient) -> None:
        """Image upload should trigger OCR and fire orchestration (mock mode)."""
        resp = await client.post(
            "/api/chat",
            json={
                "message": "",
                "session_id": "ocr-test",
                "image": "data:image/jpeg;base64,/9j/fakedata",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["intent"] == "flight_disruption"
        # Mock OCR returns all fields → should fire orchestration immediately
        assert data["status"] == "processing"
        assert "event_id" in data
        assert "boarding pass" in data["acknowledgment"].lower()

    @pytest.mark.asyncio
    async def test_ticket_pdf_download_404_when_missing(self, client: AsyncClient) -> None:
        """PDF endpoint should return 404 for unknown event."""
        resp = await client.get("/api/tickets/nonexistent/pdf")
        assert resp.status_code == 404

    @pytest.mark.asyncio
    async def test_ticket_pdf_download_after_confirm(self, client: AsyncClient) -> None:
        """After confirming a booking, PDF should be available."""
        # Trigger disruption
        resp = await client.post(
            "/api/chat",
            json={
                "message": "My flight UA 2381 from SFO to JFK got cancelled",
                "session_id": "pdf-test",
            },
        )
        data = resp.json()
        event_id = data["event_id"]

        # Wait for resolution
        for _ in range(120):
            await asyncio.sleep(0.1)
            status_resp = await client.get(f"/api/chat/status/{event_id}")
            if status_resp.json()["status"] == "complete":
                break

        # Confirm booking
        confirm_resp = await client.post(
            "/api/chat",
            json={"message": "Yes, book it", "session_id": "pdf-test"},
        )
        confirm_data = confirm_resp.json()
        assert confirm_data["resolution"]["status"] == "confirmed"
        assert confirm_data["resolution"].get("ticket_pdf_url") is not None

        # Download PDF
        pdf_url = confirm_data["resolution"]["ticket_pdf_url"]
        pdf_resp = await client.get(pdf_url)
        assert pdf_resp.status_code == 200
        assert pdf_resp.headers["content-type"] == "application/pdf"
        assert pdf_resp.content[:5] == b"%PDF-"

    @pytest.mark.asyncio
    async def test_reset_clears_gathering_state(self, client: AsyncClient) -> None:
        """Reset should clear gathering context so session starts fresh."""
        sid = "reset-gather"
        # Start gathering
        await client.post(
            "/api/chat", json={"message": "my flight got cancelled", "session_id": sid}
        )

        # Reset
        await client.post("/api/reset")

        # Same session should NOT be in gathering mode anymore
        resp = await client.post(
            "/api/chat", json={"message": "my flight got cancelled", "session_id": sid}
        )
        data = resp.json()
        # Should start fresh gathering, not treat as info_response
        assert data["intent"] == "flight_disruption"
        assert data["status"] == "gathering"

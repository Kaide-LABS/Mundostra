"""Tests for Amadeus Flight Search integration in ResearchAgent."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backend.agents.research import ResearchAgent
from backend.message_bus.bus import MessageBus

# Realistic Amadeus Flight Offers Search response fixture
AMADEUS_RESPONSE_DATA: list[dict[str, Any]] = [
    {
        "type": "flight-offer",
        "id": "1",
        "itineraries": [
            {
                "segments": [
                    {
                        "departure": {"iataCode": "SFO", "at": "2026-02-20T18:30:00"},
                        "arrival": {"iataCode": "JFK", "at": "2026-02-21T03:05:00"},
                        "carrierCode": "UA",
                        "number": "456",
                        "numberOfStops": 0,
                    }
                ]
            }
        ],
        "price": {"currency": "USD", "total": "389.50", "base": "350.00"},
    },
    {
        "type": "flight-offer",
        "id": "2",
        "itineraries": [
            {
                "segments": [
                    {
                        "departure": {"iataCode": "SFO", "at": "2026-02-20T14:00:00"},
                        "arrival": {"iataCode": "ORD", "at": "2026-02-20T20:15:00"},
                        "carrierCode": "AA",
                        "number": "789",
                        "numberOfStops": 0,
                    },
                    {
                        "departure": {"iataCode": "ORD", "at": "2026-02-20T21:30:00"},
                        "arrival": {"iataCode": "JFK", "at": "2026-02-21T00:45:00"},
                        "carrierCode": "AA",
                        "number": "1023",
                        "numberOfStops": 0,
                    },
                ]
            }
        ],
        "price": {"currency": "USD", "total": "275.00", "base": "240.00"},
    },
    {
        "type": "flight-offer",
        "id": "3",
        "itineraries": [
            {
                "segments": [
                    {
                        "departure": {"iataCode": "SFO", "at": "2026-02-20T09:00:00"},
                        "arrival": {"iataCode": "JFK", "at": "2026-02-20T17:30:00"},
                        "carrierCode": "DL",
                        "number": "100",
                        "numberOfStops": 0,
                    }
                ]
            }
        ],
        "price": {"currency": "USD", "total": "512.00", "base": "460.00"},
    },
]


def _make_agent(mock_llm: bool = True) -> ResearchAgent:
    """Create a ResearchAgent with a dummy bus."""
    bus = MessageBus()
    return ResearchAgent(bus=bus, mock_llm=mock_llm)


class TestTransformAmadeusResponse:
    """Test _transform_amadeus_response maps Amadeus data to FlightAlternative schema."""

    def setup_method(self) -> None:
        self.agent = _make_agent()

    def test_basic_nonstop_flight(self) -> None:
        result = self.agent._transform_amadeus_response([AMADEUS_RESPONSE_DATA[0]])
        assert len(result) == 1
        alt = result[0]
        assert alt["flight"] == "UA 456"
        assert alt["airline"] == "UA"
        assert alt["origin"] == "SFO"
        assert alt["destination"] == "JFK"
        assert alt["departure"] == "2026-02-20T18:30:00"
        assert alt["arrival"] == "2026-02-21T03:05:00"
        assert alt["price"] == 389.50
        assert alt["seat_available"] is True
        assert alt["cabin"] == "economy"
        assert alt["number_of_stops"] == 0

    def test_connecting_flight(self) -> None:
        """Connecting flights: first segment departure, last segment arrival, stop count."""
        result = self.agent._transform_amadeus_response([AMADEUS_RESPONSE_DATA[1]])
        assert len(result) == 1
        alt = result[0]
        assert alt["flight"] == "AA 789"  # uses first segment
        assert alt["origin"] == "SFO"
        assert alt["destination"] == "JFK"  # uses last segment arrival
        assert alt["departure"] == "2026-02-20T14:00:00"
        assert alt["arrival"] == "2026-02-21T00:45:00"
        assert alt["number_of_stops"] == 1

    def test_multiple_offers(self) -> None:
        result = self.agent._transform_amadeus_response(AMADEUS_RESPONSE_DATA)
        assert len(result) == 3
        prices = [alt["price"] for alt in result]
        assert prices == [389.50, 275.00, 512.00]

    def test_empty_response(self) -> None:
        result = self.agent._transform_amadeus_response([])
        assert result == []

    def test_price_is_float(self) -> None:
        """Amadeus returns price as string; we must convert to float."""
        result = self.agent._transform_amadeus_response([AMADEUS_RESPONSE_DATA[2]])
        assert isinstance(result[0]["price"], float)
        assert result[0]["price"] == 512.0


class TestAmadeusConfigured:
    """Test _amadeus_configured() checks credentials."""

    @patch("backend.agents.research.get_settings")
    def test_not_configured_by_default(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value = MagicMock(
            amadeus_client_id="",
            amadeus_client_secret="",
            amadeus_env="test",
            research_model_id="gemini-2.5-flash",
        )
        agent = _make_agent()
        assert agent._amadeus_configured() is False

    @patch("backend.agents.research.get_settings")
    def test_configured_with_credentials(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value = MagicMock(
            amadeus_client_id="test_id",
            amadeus_client_secret="test_secret",
            amadeus_env="test",
            research_model_id="gemini-2.5-flash",
        )
        agent = _make_agent(mock_llm=False)
        assert agent._amadeus_configured() is True

    @patch("backend.agents.research.get_settings")
    def test_not_configured_partial_credentials(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value = MagicMock(
            amadeus_client_id="test_id",
            amadeus_client_secret="",
            amadeus_env="test",
            research_model_id="gemini-2.5-flash",
        )
        agent = _make_agent(mock_llm=False)
        assert agent._amadeus_configured() is False


class TestAmadeusSearchFallback:
    """Test that Amadeus failure falls back to mock API."""

    @pytest.mark.asyncio
    @patch("backend.agents.research.get_settings")
    async def test_amadeus_failure_falls_back_to_mock(self, mock_settings: MagicMock) -> None:
        mock_settings.return_value = MagicMock(
            amadeus_client_id="test_id",
            amadeus_client_secret="test_secret",
            amadeus_env="test",
            research_model_id="gemini-2.5-flash",
            base_url="http://test",
        )
        agent = _make_agent(mock_llm=False)
        agent.emit_trace = AsyncMock()  # type: ignore[method-assign]
        # Mock LLM call so we don't hit real Vertex AI
        agent._call_llm = AsyncMock(return_value='{"alternatives": [], "recommendation": "test"}')  # type: ignore[method-assign]

        # Mock _search_amadeus to raise an exception
        agent._search_amadeus = AsyncMock(side_effect=Exception("API rate limited"))  # type: ignore[method-assign]

        # Mock _search_mock to return data
        mock_alternatives = [
            {
                "flight": "UA105",
                "departure": "2026-02-20T18:30:00",
                "arrival": "2026-02-20T23:45:00",
                "price": 420.0,
                "seat_available": True,
            }
        ]
        agent._search_mock = AsyncMock(return_value=mock_alternatives)  # type: ignore[method-assign]

        # Mock http client for calendar check
        mock_cal_response = MagicMock()
        mock_cal_response.json.return_value = {"has_conflict": False, "conflict_details": None}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_cal_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)
        agent._make_http_client = MagicMock(return_value=mock_client)  # type: ignore[method-assign]

        from backend.models.tasks import AgentName, AgentTask

        task = AgentTask(
            event_id="00000000-0000-0000-0000-000000000001",
            agent=AgentName.RESEARCH,
            input_data={
                "flight": {"origin": "SFO", "destination": "JFK", "original_price": 400.0},
                "traveler": {"email": "test@test.com"},
            },
        )

        result = await agent.run(task)

        # Should have fallen back to mock and produced a result
        assert "alternatives" in result
        assert "recommendation" in result
        # Verify _search_mock was called (fallback path)
        agent._search_mock.assert_called_once()

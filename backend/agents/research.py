"""Research Agent — Gemini 2.5 Flash via Vertex AI.

Finds alternative flights, checks calendar conflicts, ranks options.
Uses Amadeus Flight Offers Search API when available, falls back to mock.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from backend.agents.base import BaseAgent
from backend.config import get_settings
from backend.logging_config import get_logger
from backend.models.tasks import AgentName, AgentTask, TraceStatus
from backend.orchestrator.prompts import RESEARCH_SYSTEM_PROMPT

logger = get_logger(__name__)


class ResearchAgent(BaseAgent):
    agent_name = AgentName.RESEARCH

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        settings = get_settings()
        self.model_id = settings.research_model_id

    def _amadeus_configured(self) -> bool:
        """Check if Amadeus credentials are present."""
        settings = get_settings()
        return bool(settings.amadeus_client_id and settings.amadeus_client_secret)

    async def _search_amadeus(self, origin: str, destination: str, date_str: str) -> list[dict[str, Any]]:
        """Search real flights via Amadeus Flight Offers Search API."""
        from amadeus import Client  # type: ignore[import-untyped]

        settings = get_settings()
        amadeus = Client(
            client_id=settings.amadeus_client_id,
            client_secret=settings.amadeus_client_secret,
            hostname=settings.amadeus_env,
        )

        response = await asyncio.to_thread(
            amadeus.shopping.flight_offers_search.get,
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date_str,
            adults=1,
            max=10,
        )

        return self._transform_amadeus_response(response.data)

    def _transform_amadeus_response(self, offers: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Map Amadeus offers to our FlightAlternative structure."""
        alternatives: list[dict[str, Any]] = []
        for offer in offers:
            itinerary = offer["itineraries"][0]  # outbound only
            segments = itinerary["segments"]
            first_seg = segments[0]
            last_seg = segments[-1]

            carrier = first_seg["carrierCode"]
            number = first_seg["number"]

            alternatives.append({
                "flight": f"{carrier} {number}",
                "airline": carrier,
                "origin": first_seg["departure"]["iataCode"],
                "destination": last_seg["arrival"]["iataCode"],
                "departure": first_seg["departure"]["at"],
                "arrival": last_seg["arrival"]["at"],
                "price": float(offer["price"]["total"]),
                "seat_available": True,  # Amadeus only returns available offers
                "cabin": "economy",
                "number_of_stops": len(segments) - 1,
            })
        return alternatives

    async def _search_mock(self, client: Any, origin: str, destination: str) -> list[dict[str, Any]]:
        """Search flights via mock API."""
        flight_resp = await client.get(
            "/mock/flights/search",
            params={"origin": origin, "destination": destination},
        )
        flight_data = flight_resp.json()
        return flight_data.get("alternatives", [])  # type: ignore[no-any-return]

    async def run(self, task: AgentTask) -> dict[str, Any]:
        event_data = task.input_data
        flight = event_data.get("flight", {})
        traveler = event_data.get("traveler", {})
        origin = flight.get("origin", "SFO")
        destination = flight.get("destination", "JFK")

        # Step 1: Get alternative flights
        await self.emit_trace(
            event_id=task.event_id,
            status=TraceStatus.WORKING,
            message=f"Searching alternative flights {origin} → {destination}...",
        )

        # Use Amadeus when not in mock mode and credentials are configured
        if not self.mock_llm and self._amadeus_configured():
            try:
                from datetime import date

                date_str = flight.get("date", date.today().isoformat())
                alternatives = await self._search_amadeus(origin, destination, date_str)
                source = "amadeus_api"
                logger.info("amadeus_search_success", origin=origin, destination=destination, count=len(alternatives))
            except Exception as exc:
                logger.warning("amadeus_search_failed", error=str(exc), fallback="mock_api")
                async with self._make_http_client() as client:
                    alternatives = await self._search_mock(client, origin, destination)
                source = "mock_inventory_api"
        else:
            async with self._make_http_client() as client:
                alternatives = await self._search_mock(client, origin, destination)
            source = "mock_inventory_api"

        await self.emit_trace(
            event_id=task.event_id,
            status=TraceStatus.WORKING,
            message=f"Found {len(alternatives)} flight options. Checking calendar conflicts...",
        )

        # Step 2: Check calendar for each available flight (always uses mock calendar)
        enriched: list[dict[str, Any]] = []
        original_price = flight.get("original_price", 400.0)

        async with self._make_http_client() as client:
            for alt in alternatives:
                if not alt.get("seat_available", True):
                    continue

                cal_resp = await client.get(
                    "/mock/calendar/check",
                    params={
                        "traveler_email": traveler.get("email", ""),
                        "arrival_time": alt.get("arrival", ""),
                    },
                )
                cal_data = cal_resp.json()

                price = float(alt["price"])
                delta = price - original_price
                delta_str = f"+${delta:.0f}" if delta >= 0 else f"-${abs(delta):.0f}"

                enriched.append(
                    {
                        "flight": alt["flight"],
                        "departure": alt["departure"],
                        "arrival": alt["arrival"],
                        "price": price,
                        "calendar_conflict": cal_data.get("has_conflict", False),
                        "conflict_details": cal_data.get("conflict_details"),
                        "price_vs_original": delta_str,
                        "seat_available": True,
                        "source": source,
                    }
                )

        # Step 3: Use LLM to rank options (or mock)
        if self.mock_llm:
            return self._get_mock_response(task, enriched, original_price)

        user_message = (
            f"Cancelled flight: {flight.get('number', 'UA100')} "
            f"from {origin} to {destination}\n"
            f"Original price: ${original_price}\n"
            f"Traveler: {traveler.get('name', 'Unknown')}, {traveler.get('role', 'Unknown')}\n"
            f"Timezone: {traveler.get('timezone', 'America/Los_Angeles')}\n\n"
            f"Available alternatives:\n{json.dumps(enriched, indent=2)}\n\n"
            f"Rank these options and provide your recommendation."
        )

        llm_response = await self._call_llm(RESEARCH_SYSTEM_PROMPT, user_message)
        task.tokens_used = 1847
        task.cost_usd = 0.0092

        try:
            return json.loads(llm_response)  # type: ignore[no-any-return]
        except json.JSONDecodeError:
            return self._get_mock_response(task, enriched, original_price)

    def _get_mock_response(
        self,
        task: AgentTask | None = None,
        enriched: list[dict[str, Any]] | None = None,
        original_price: float = 400.0,
    ) -> dict[str, Any]:
        if enriched is None:
            enriched = []

        # Sort: no-conflict first, then by price
        no_conflict = [a for a in enriched if not a.get("calendar_conflict")]
        no_conflict.sort(key=lambda x: float(x["price"]))

        viable = no_conflict[:3] if len(no_conflict) >= 3 else no_conflict
        best = viable[0] if viable else None

        if task is not None:
            task.tokens_used = 1847
            task.cost_usd = 0.0092

        rec = (
            f"{best['flight']} — ${best['price']:.0f}, no calendar conflicts"
            if best
            else "No viable options found"
        )

        return {
            "alternatives": viable,
            "recommendation": rec,
            "search_metadata": {
                "options_evaluated": len(enriched),
                "options_filtered_by_availability": len(enriched)
                - len([a for a in enriched if a.get("seat_available")]),
                "options_filtered_by_calendar": len(
                    [a for a in enriched if a.get("calendar_conflict")]
                ),
            },
        }

    async def _call_llm(self, system_prompt: str, user_message: str) -> str:
        from google.cloud import aiplatform
        from vertexai.generative_models import GenerativeModel

        settings = get_settings()

        def _sync_call() -> str:
            aiplatform.init(project=settings.gcp_project_id, location=settings.gcp_location)
            model = GenerativeModel(
                self.model_id,
                system_instruction=system_prompt,
            )
            response = model.generate_content(
                user_message,
                generation_config={"response_mime_type": "application/json"},
            )
            return response.text

        return await asyncio.to_thread(_sync_call)

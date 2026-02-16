"""Mock flight inventory API — simulates Amadeus/Duffel."""

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Query

router = APIRouter(prefix="/mock/flights", tags=["mock"])

# Base time: 2 hours from "now" for the demo scenario
_BASE_DEPARTURE = datetime(2025, 2, 12, 18, 30, 0)


def _build_alternatives(origin: str, destination: str) -> list[dict[str, object]]:
    """7 deterministic flight alternatives: varying airlines, prices, one red-eye, one over-budget."""
    return [
        {
            "flight": "UA105",
            "airline": "United Airlines",
            "origin": origin,
            "destination": destination,
            "departure": _BASE_DEPARTURE.isoformat(),
            "arrival": (_BASE_DEPARTURE + timedelta(hours=5, minutes=15)).isoformat(),
            "price": 420.0,
            "seat_available": True,
            "cabin": "economy",
        },
        {
            "flight": "AA210",
            "airline": "American Airlines",
            "origin": origin,
            "destination": destination,
            "departure": (_BASE_DEPARTURE + timedelta(minutes=45)).isoformat(),
            "arrival": (_BASE_DEPARTURE + timedelta(hours=6)).isoformat(),
            "price": 385.0,
            "seat_available": True,
            "cabin": "economy",
        },
        {
            "flight": "DL450",
            "airline": "Delta Air Lines",
            "origin": origin,
            "destination": destination,
            "departure": (_BASE_DEPARTURE + timedelta(hours=1, minutes=30)).isoformat(),
            "arrival": (_BASE_DEPARTURE + timedelta(hours=6, minutes=45)).isoformat(),
            "price": 450.0,
            "seat_available": True,
            "cabin": "economy",
        },
        {
            "flight": "B6320",
            "airline": "JetBlue",
            "origin": origin,
            "destination": destination,
            "departure": (_BASE_DEPARTURE + timedelta(hours=2)).isoformat(),
            "arrival": (_BASE_DEPARTURE + timedelta(hours=7, minutes=20)).isoformat(),
            "price": 340.0,
            "seat_available": True,
            "cabin": "economy",
        },
        {
            "flight": "UA900",
            "airline": "United Airlines",
            "origin": origin,
            "destination": destination,
            "departure": (_BASE_DEPARTURE + timedelta(hours=4, minutes=30)).isoformat(),
            "arrival": (_BASE_DEPARTURE + timedelta(hours=9, minutes=30)).isoformat(),
            "price": 310.0,
            "seat_available": True,
            "cabin": "economy",
            "note": "red-eye",
        },
        {
            "flight": "AA550",
            "airline": "American Airlines",
            "origin": origin,
            "destination": destination,
            "departure": (_BASE_DEPARTURE + timedelta(minutes=20)).isoformat(),
            "arrival": (_BASE_DEPARTURE + timedelta(hours=5, minutes=35)).isoformat(),
            "price": 680.0,
            "seat_available": True,
            "cabin": "business",
            "note": "business class upgrade",
        },
        {
            "flight": "DL800",
            "airline": "Delta Air Lines",
            "origin": origin,
            "destination": destination,
            "departure": (_BASE_DEPARTURE + timedelta(hours=3)).isoformat(),
            "arrival": (_BASE_DEPARTURE + timedelta(hours=8, minutes=15)).isoformat(),
            "price": 395.0,
            "seat_available": False,
            "cabin": "economy",
        },
    ]


@router.get("/search")
async def search_flights(
    origin: str = Query(default="SFO"),
    destination: str = Query(default="JFK"),
    date: str = Query(default="2025-02-12"),
) -> dict[str, object]:
    alternatives = _build_alternatives(origin, destination)
    return {
        "origin": origin,
        "destination": destination,
        "date": date,
        "results_count": len(alternatives),
        "alternatives": alternatives,
    }

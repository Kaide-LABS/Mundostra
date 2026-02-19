"""Mock flight inventory API — simulates Amadeus/Duffel."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Query

router = APIRouter(prefix="/mock/flights", tags=["mock"])


def _get_base_departure() -> datetime:
    """Today at 18:30 — keeps the demo feeling live."""
    today = date.today()
    return datetime(today.year, today.month, today.day, 18, 30, 0)


def _build_alternatives(origin: str, destination: str) -> list[dict[str, object]]:
    """7 deterministic flight alternatives: varying airlines, prices, one red-eye, one over-budget."""
    base = _get_base_departure()
    return [
        {
            "flight": "UA105",
            "airline": "United Airlines",
            "origin": origin,
            "destination": destination,
            "departure": base.isoformat(),
            "arrival": (base + timedelta(hours=5, minutes=15)).isoformat(),
            "price": 420.0,
            "seat_available": True,
            "cabin": "economy",
        },
        {
            "flight": "AA210",
            "airline": "American Airlines",
            "origin": origin,
            "destination": destination,
            "departure": (base + timedelta(minutes=45)).isoformat(),
            "arrival": (base + timedelta(hours=6)).isoformat(),
            "price": 385.0,
            "seat_available": True,
            "cabin": "economy",
        },
        {
            "flight": "DL450",
            "airline": "Delta Air Lines",
            "origin": origin,
            "destination": destination,
            "departure": (base + timedelta(hours=1, minutes=30)).isoformat(),
            "arrival": (base + timedelta(hours=6, minutes=45)).isoformat(),
            "price": 450.0,
            "seat_available": True,
            "cabin": "economy",
        },
        {
            "flight": "B6320",
            "airline": "JetBlue",
            "origin": origin,
            "destination": destination,
            "departure": (base + timedelta(hours=2)).isoformat(),
            "arrival": (base + timedelta(hours=7, minutes=20)).isoformat(),
            "price": 340.0,
            "seat_available": True,
            "cabin": "economy",
        },
        {
            "flight": "UA900",
            "airline": "United Airlines",
            "origin": origin,
            "destination": destination,
            "departure": (base + timedelta(hours=4, minutes=30)).isoformat(),
            "arrival": (base + timedelta(hours=9, minutes=30)).isoformat(),
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
            "departure": (base + timedelta(minutes=20)).isoformat(),
            "arrival": (base + timedelta(hours=5, minutes=35)).isoformat(),
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
            "departure": (base + timedelta(hours=3)).isoformat(),
            "arrival": (base + timedelta(hours=8, minutes=15)).isoformat(),
            "price": 395.0,
            "seat_available": False,
            "cabin": "economy",
        },
    ]


@router.get("/search")
async def search_flights(
    origin: str = Query(default="SFO"),
    destination: str = Query(default="JFK"),
    search_date: str = Query(default="", alias="date"),
) -> dict[str, object]:
    effective_date = search_date or date.today().isoformat()
    alternatives = _build_alternatives(origin, destination)
    return {
        "origin": origin,
        "destination": destination,
        "date": effective_date,
        "results_count": len(alternatives),
        "alternatives": alternatives,
    }

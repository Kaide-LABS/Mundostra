"""Mock calendar API — simulates Google Calendar."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from fastapi import APIRouter, Query

router = APIRouter(prefix="/mock/calendar", tags=["mock"])


def _get_meetings() -> list[dict[str, str]]:
    """Board meeting tomorrow 10 AM ET, standup tomorrow 2 PM ET — always relative to today."""
    tomorrow = date.today() + timedelta(days=1)
    return [
        {
            "title": "Board Meeting",
            "start": f"{tomorrow.isoformat()}T10:00:00-05:00",
            "end": f"{tomorrow.isoformat()}T12:00:00-05:00",
            "location": "Manhattan HQ, Conference Room A",
            "importance": "critical",
        },
        {
            "title": "Team Standup",
            "start": f"{tomorrow.isoformat()}T14:00:00-05:00",
            "end": f"{tomorrow.isoformat()}T14:30:00-05:00",
            "location": "Virtual",
            "importance": "normal",
        },
    ]


def _default_arrival_time() -> str:
    """Today at 23:45 — evening arrival, no calendar conflict."""
    today = date.today()
    return datetime(today.year, today.month, today.day, 23, 45, 0).isoformat()


@router.get("/check")
async def check_calendar(
    traveler_email: str = Query(default="sarah@designpartner.com"),
    arrival_time: str = Query(default=""),
    timezone: str = Query(default="America/New_York"),
) -> dict[str, object]:
    effective_arrival = arrival_time or _default_arrival_time()
    try:
        arrival = datetime.fromisoformat(effective_arrival)
    except ValueError:
        arrival = datetime.fromisoformat(_default_arrival_time())

    # Board meeting is at 10 AM ET tomorrow — need to arrive by ~8 AM to be safe
    tomorrow = date.today() + timedelta(days=1)
    cutoff = datetime(tomorrow.year, tomorrow.month, tomorrow.day, 8, 0, 0)
    has_conflict = arrival > cutoff

    meetings = _get_meetings()
    return {
        "traveler_email": traveler_email,
        "arrival_time": effective_arrival,
        "timezone": timezone,
        "meetings": meetings,
        "has_conflict": has_conflict,
        "conflict_details": (
            "Arrival after 8:00 AM ET conflicts with 10:00 AM Board Meeting"
            if has_conflict
            else None
        ),
        "next_critical_meeting": meetings[0],
    }

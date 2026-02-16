"""Mock calendar API — simulates Google Calendar."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Query

router = APIRouter(prefix="/mock/calendar", tags=["mock"])

# Sarah's 10 AM board meeting in NYC creates conflict for late arrivals
_MEETINGS = [
    {
        "title": "Board Meeting",
        "start": "2025-02-13T10:00:00-05:00",
        "end": "2025-02-13T12:00:00-05:00",
        "location": "Manhattan HQ, Conference Room A",
        "importance": "critical",
    },
    {
        "title": "Team Standup",
        "start": "2025-02-13T14:00:00-05:00",
        "end": "2025-02-13T14:30:00-05:00",
        "location": "Virtual",
        "importance": "normal",
    },
]


@router.get("/check")
async def check_calendar(
    traveler_email: str = Query(default="sarah@designpartner.com"),
    arrival_time: str = Query(default="2025-02-12T23:45:00"),
    timezone: str = Query(default="America/New_York"),
) -> dict[str, object]:
    try:
        arrival = datetime.fromisoformat(arrival_time)
    except ValueError:
        arrival = datetime(2025, 2, 12, 23, 45, 0)

    # Board meeting is at 10 AM ET on Feb 13 — need to arrive by ~8 AM to be safe
    cutoff = datetime(2025, 2, 13, 8, 0, 0)
    has_conflict = arrival > cutoff

    return {
        "traveler_email": traveler_email,
        "arrival_time": arrival_time,
        "timezone": timezone,
        "meetings": _MEETINGS,
        "has_conflict": has_conflict,
        "conflict_details": (
            "Arrival after 8:00 AM ET conflicts with 10:00 AM Board Meeting"
            if has_conflict
            else None
        ),
        "next_critical_meeting": _MEETINGS[0],
    }

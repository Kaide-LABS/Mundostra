"""Tests for Gmail HTML email builders."""

from __future__ import annotations

from backend.gmail.emails import (
    build_confirmation_email,
    build_options_email,
    build_resolution_email,
)


def test_resolution_email_structure() -> None:
    """Resolution email has subject and html_body with key details."""
    email = build_resolution_email(
        event_id="test-event-123",
        traveler_name="Sarah Chen",
        cancelled_flight="UA100",
        origin="SFO",
        destination="JFK",
        chosen_flight="UA105",
        departure="6:30 PM",
        arrival="11:45 PM",
        price=420.0,
        price_delta="+$20",
        confidence=0.94,
        message_text="Hi Sarah — your flight has been rebooked.",
    )

    assert "subject" in email
    assert "html_body" in email
    assert "Sarah Chen" in email["subject"]
    assert "Hi Sarah" in email["html_body"]
    assert "94%" in email["html_body"]


def test_resolution_email_contains_flight_details() -> None:
    """Resolution email HTML contains the flight details."""
    email = build_resolution_email(
        event_id="abc-123-def",
        traveler_name="Sarah",
        cancelled_flight="UA100",
        origin="SFO",
        destination="JFK",
        chosen_flight="UA105",
        departure="6:30 PM",
        arrival="11:45 PM",
        price=420.0,
        price_delta="+$20",
        confidence=0.94,
        message_text="Test message",
    )

    body = email["html_body"]
    assert "UA100" in body
    assert "UA105" in body
    assert "$420.00" in body
    assert "+$20" in body


def test_confirmation_email_structure() -> None:
    """Confirmation email has correct subject and green confirmation."""
    email = build_confirmation_email(
        traveler_name="Sarah Chen",
        chosen_flight="UA105",
        departure="6:30 PM",
    )

    assert "Confirmed" in email["subject"]
    assert "Sarah Chen" in email["html_body"]
    assert "Booking Confirmed" in email["html_body"]


def test_options_email_lists_alternatives() -> None:
    """Options email lists alternatives."""
    alternatives = [
        {"flight": "UA105", "departure": "6:30 PM", "price": 420.0, "calendar_conflict": False},
        {"flight": "UA107", "departure": "8:00 PM", "price": 380.0, "calendar_conflict": True},
    ]

    email = build_options_email(
        traveler_name="Sarah Chen",
        alternatives=alternatives,
    )

    assert "Sarah Chen" in email["subject"]
    assert "UA105" in email["html_body"]
    assert "UA107" in email["html_body"]
    assert "calendar conflict" in email["html_body"]

"""Tests for Microsoft Teams Adaptive Card builders."""

from __future__ import annotations

from backend.teams.cards import (
    build_confirmation_card,
    build_options_card,
    build_resolution_card,
)


def test_resolution_card_structure() -> None:
    """Resolution card has Adaptive Card with header, message, columns, and confidence."""
    card = build_resolution_card(
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

    assert card["type"] == "message"
    attachment = card["attachments"][0]
    assert attachment["contentType"] == "application/vnd.microsoft.card.adaptive"
    content = attachment["content"]
    assert content["type"] == "AdaptiveCard"
    assert content["version"] == "1.4"
    # Header + message + 3 ColumnSets + confidence = 6 body items
    assert len(content["body"]) == 6


def test_resolution_card_contains_flight_details() -> None:
    """Resolution card body contains the flight details."""
    card = build_resolution_card(
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

    content = card["attachments"][0]["content"]
    # Header should mention traveler
    assert "Sarah" in content["body"][0]["text"]
    # Confidence line
    assert "94%" in content["body"][5]["text"]


def test_confirmation_card_structure() -> None:
    """Confirmation card has correct heading and body."""
    card = build_confirmation_card(
        traveler_name="Sarah Chen",
        chosen_flight="UA105",
        departure="6:30 PM",
    )

    content = card["attachments"][0]["content"]
    assert content["type"] == "AdaptiveCard"
    assert any("Confirmed" in item.get("text", "") for item in content["body"])


def test_options_card_lists_alternatives() -> None:
    """Options card lists alternatives by number."""
    alternatives = [
        {"flight": "UA105", "departure": "6:30 PM", "price": 420.0, "calendar_conflict": False},
        {"flight": "UA107", "departure": "8:00 PM", "price": 380.0, "calendar_conflict": True},
    ]

    card = build_options_card(
        traveler_name="Sarah Chen",
        alternatives=alternatives,
    )

    content = card["attachments"][0]["content"]
    body_text = content["body"][1]["text"]
    assert "UA105" in body_text
    assert "UA107" in body_text
    assert "calendar conflict" in body_text

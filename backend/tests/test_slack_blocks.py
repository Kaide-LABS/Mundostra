"""Tests for Slack Block Kit message builders."""

from __future__ import annotations

from backend.slack.blocks import (
    build_confirmation_update,
    build_options_update,
    build_resolution_message,
)


def test_resolution_message_structure() -> None:
    """Resolution message has section, divider, fields, context, and actions blocks."""
    blocks = build_resolution_message(
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

    assert len(blocks) == 5
    assert blocks[0]["type"] == "section"
    assert blocks[1]["type"] == "divider"
    assert blocks[2]["type"] == "section"
    assert blocks[3]["type"] == "context"
    assert blocks[4]["type"] == "actions"


def test_resolution_message_has_event_id_in_buttons() -> None:
    """Button values contain the event_id for routing responses."""
    event_id = "abc-123-def"
    blocks = build_resolution_message(
        event_id=event_id,
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

    actions = blocks[4]
    assert actions["type"] == "actions"
    buttons = actions["elements"]
    assert len(buttons) == 2

    # Both buttons should have the event_id as value
    assert buttons[0]["value"] == event_id
    assert buttons[1]["value"] == event_id
    assert buttons[0]["action_id"] == "traveler_confirm"
    assert buttons[1]["action_id"] == "traveler_options"


def test_confirmation_update_removes_buttons() -> None:
    """Confirmation update has no action blocks (buttons removed)."""
    blocks = build_confirmation_update(
        traveler_name="Sarah Chen",
        chosen_flight="UA105",
        departure="6:30 PM",
    )

    block_types = [b["type"] for b in blocks]
    assert "actions" not in block_types
    assert "section" in block_types
    # Should mention confirmed
    text = blocks[0]["text"]["text"]
    assert "Confirmed" in text


def test_options_update_lists_alternatives() -> None:
    """Options update lists alternatives by number."""
    alternatives = [
        {"flight": "UA105", "departure": "6:30 PM", "price": 420.0, "calendar_conflict": False},
        {"flight": "UA107", "departure": "8:00 PM", "price": 380.0, "calendar_conflict": True},
    ]

    blocks = build_options_update(
        traveler_name="Sarah Chen",
        alternatives=alternatives,
    )

    text = blocks[0]["text"]["text"]
    assert "UA105" in text
    assert "UA107" in text
    assert "calendar conflict" in text

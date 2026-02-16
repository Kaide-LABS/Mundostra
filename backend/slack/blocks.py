"""Slack Block Kit message builders."""

from __future__ import annotations

from typing import Any


def build_resolution_message(
    *,
    event_id: str,
    traveler_name: str,
    cancelled_flight: str,
    origin: str,
    destination: str,
    chosen_flight: str,
    departure: str,
    arrival: str,
    price: float,
    price_delta: str,
    confidence: float,
    message_text: str,
) -> list[dict[str, Any]]:
    """Build Block Kit blocks for a resolution proposal sent to the traveler."""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message_text,
            },
        },
        {
            "type": "divider",
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Cancelled:*\n{cancelled_flight}"},
                {"type": "mrkdwn", "text": f"*Route:*\n{origin} -> {destination}"},
                {"type": "mrkdwn", "text": f"*Rebooked:*\n{chosen_flight}"},
                {"type": "mrkdwn", "text": f"*Price:*\n${price:.2f} ({price_delta})"},
                {"type": "mrkdwn", "text": f"*Departure:*\n{departure}"},
                {"type": "mrkdwn", "text": f"*Arrival:*\n{arrival}"},
            ],
        },
        {
            "type": "context",
            "elements": [
                {
                    "type": "mrkdwn",
                    "text": f"Confidence: {confidence:.0%} | Mundostra Travel OS",
                },
            ],
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Confirm Booking"},
                    "style": "primary",
                    "action_id": "traveler_confirm",
                    "value": event_id,
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "See Options"},
                    "action_id": "traveler_options",
                    "value": event_id,
                },
            ],
        },
    ]


def build_confirmation_update(
    *,
    traveler_name: str,
    chosen_flight: str,
    departure: str,
) -> list[dict[str, Any]]:
    """Replace the original message blocks after traveler confirms booking."""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f":white_check_mark: *Booking Confirmed*\n"
                    f"{traveler_name} — {chosen_flight} departing {departure}\n"
                    f"Your card has been authorized and the seat is reserved."
                ),
            },
        },
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": "Mundostra Travel OS — confirmed"},
            ],
        },
    ]


def build_options_update(
    *,
    traveler_name: str,
    alternatives: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Replace the original message blocks when traveler asks for options."""
    alt_lines = []
    for i, alt in enumerate(alternatives[:5], 1):
        flight = alt.get("flight", "???")
        dep = alt.get("departure", "")
        price = alt.get("price", 0)
        conflict = " :warning: calendar conflict" if alt.get("calendar_conflict") else ""
        alt_lines.append(f"{i}. *{flight}* — ${price:.2f} dep {dep}{conflict}")

    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f":mag: *Available Alternatives for {traveler_name}*\n\n"
                    + "\n".join(alt_lines)
                    + "\n\nReply with the number to select, or contact support."
                ),
            },
        },
        {
            "type": "context",
            "elements": [
                {"type": "mrkdwn", "text": "Mundostra Travel OS — options"},
            ],
        },
    ]

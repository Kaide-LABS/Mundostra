"""Microsoft Teams Adaptive Card builders."""

from __future__ import annotations

from typing import Any


def build_resolution_card(
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
) -> dict[str, Any]:
    """Build an Adaptive Card for a resolution proposal."""
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Medium",
                            "weight": "Bolder",
                            "text": f"Flight Resolution for {traveler_name}",
                            "style": "heading",
                        },
                        {
                            "type": "TextBlock",
                            "text": message_text,
                            "wrap": True,
                        },
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Cancelled",
                                            "weight": "Bolder",
                                            "size": "Small",
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": cancelled_flight,
                                            "spacing": "None",
                                        },
                                    ],
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Route",
                                            "weight": "Bolder",
                                            "size": "Small",
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": f"{origin} \u2192 {destination}",
                                            "spacing": "None",
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Rebooked",
                                            "weight": "Bolder",
                                            "size": "Small",
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": chosen_flight,
                                            "spacing": "None",
                                        },
                                    ],
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Price",
                                            "weight": "Bolder",
                                            "size": "Small",
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": f"${price:.2f} ({price_delta})",
                                            "spacing": "None",
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "ColumnSet",
                            "columns": [
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Departure",
                                            "weight": "Bolder",
                                            "size": "Small",
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": departure,
                                            "spacing": "None",
                                        },
                                    ],
                                },
                                {
                                    "type": "Column",
                                    "width": "stretch",
                                    "items": [
                                        {
                                            "type": "TextBlock",
                                            "text": "Arrival",
                                            "weight": "Bolder",
                                            "size": "Small",
                                        },
                                        {
                                            "type": "TextBlock",
                                            "text": arrival,
                                            "spacing": "None",
                                        },
                                    ],
                                },
                            ],
                        },
                        {
                            "type": "TextBlock",
                            "text": f"Confidence: {confidence:.0%} | Mundostra Travel OS",
                            "size": "Small",
                            "isSubtle": True,
                            "spacing": "Medium",
                        },
                    ],
                },
            }
        ],
    }


def build_confirmation_card(
    *,
    traveler_name: str,
    chosen_flight: str,
    departure: str,
) -> dict[str, Any]:
    """Build an Adaptive Card for booking confirmation."""
    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Medium",
                            "weight": "Bolder",
                            "text": "Booking Confirmed",
                            "color": "Good",
                        },
                        {
                            "type": "TextBlock",
                            "text": (
                                f"{traveler_name} — {chosen_flight} departing {departure}\n"
                                f"Your card has been authorized and the seat is reserved."
                            ),
                            "wrap": True,
                        },
                        {
                            "type": "TextBlock",
                            "text": "Mundostra Travel OS — confirmed",
                            "size": "Small",
                            "isSubtle": True,
                        },
                    ],
                },
            }
        ],
    }


def build_options_card(
    *,
    traveler_name: str,
    alternatives: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build an Adaptive Card listing alternatives."""
    alt_lines = []
    for i, alt in enumerate(alternatives[:5], 1):
        flight = alt.get("flight", "???")
        dep = alt.get("departure", "")
        price = alt.get("price", 0)
        conflict = " \u26a0 calendar conflict" if alt.get("calendar_conflict") else ""
        alt_lines.append(f"{i}. **{flight}** — ${price:.2f} dep {dep}{conflict}")

    return {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.4",
                    "body": [
                        {
                            "type": "TextBlock",
                            "size": "Medium",
                            "weight": "Bolder",
                            "text": f"Available Alternatives for {traveler_name}",
                        },
                        {
                            "type": "TextBlock",
                            "text": "\n\n".join(alt_lines),
                            "wrap": True,
                        },
                        {
                            "type": "TextBlock",
                            "text": "Mundostra Travel OS — options",
                            "size": "Small",
                            "isSubtle": True,
                        },
                    ],
                },
            }
        ],
    }

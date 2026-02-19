"""Microsoft Teams integration — Adaptive Cards and webhook sender."""

from backend.teams.cards import (
    build_confirmation_card,
    build_options_card,
    build_resolution_card,
)
from backend.teams.sender import TeamsSender

__all__ = [
    "TeamsSender",
    "build_confirmation_card",
    "build_options_card",
    "build_resolution_card",
]

"""Slack integration package — Block Kit messages, sender, and Bolt app."""

from backend.slack.blocks import (
    build_confirmation_update,
    build_options_update,
    build_resolution_message,
)
from backend.slack.sender import SlackSender

__all__ = [
    "SlackSender",
    "build_confirmation_update",
    "build_options_update",
    "build_resolution_message",
]

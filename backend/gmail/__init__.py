"""Gmail integration — HTML emails via SMTP."""

from backend.gmail.emails import (
    build_confirmation_email,
    build_options_email,
    build_resolution_email,
)
from backend.gmail.sender import GmailSender

__all__ = [
    "GmailSender",
    "build_confirmation_email",
    "build_options_email",
    "build_resolution_email",
]

"""Pydantic models for traveler responses to resolution proposals."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel


class TravelerResponseType(StrEnum):
    CONFIRM = "confirm"
    OPTIONS = "options"
    REJECT = "reject"


class TravelerResponse(BaseModel):
    event_id: str
    response_type: TravelerResponseType

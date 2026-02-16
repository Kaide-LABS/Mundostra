"""Pydantic models for travel disruption events."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class EventType(StrEnum):
    FLIGHT_CANCELLED = "flight_cancelled"
    FLIGHT_DELAYED = "flight_delayed"
    CARD_DECLINED = "card_declined"
    HOTEL_OVERBOOKED = "hotel_overbooked"


class PolicyTier(StrEnum):
    STANDARD = "standard"
    MANAGER = "manager"
    EXECUTIVE = "executive"


class FlightDetails(BaseModel):
    number: str
    origin: str
    destination: str
    scheduled_departure: datetime
    status: str
    reason: str | None = None
    original_price: float = 400.0


class TravelerProfile(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    email: str
    role: str
    policy_tier: PolicyTier
    slack_id: str
    timezone: str = "America/Los_Angeles"
    calendar_integration: bool = True
    preferences: dict[str, Any] = Field(default_factory=dict)


class TravelEvent(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    booking_ref: str
    flight: FlightDetails | None = None
    traveler: TravelerProfile
    metadata: dict[str, Any] = Field(default_factory=dict)

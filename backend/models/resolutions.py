"""Pydantic models for resolution outputs."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class ResolutionStatus(StrEnum):
    PROPOSED = "proposed"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    ESCALATED = "escalated"


class FlightAlternative(BaseModel):
    flight: str
    departure: datetime
    arrival: datetime
    price: float
    calendar_conflict: bool = False
    conflict_details: str | None = None
    price_vs_original: str = ""
    seat_available: bool = True
    source: str = "mock_inventory_api"


class ResearchResult(BaseModel):
    alternatives: list[FlightAlternative] = Field(default_factory=list)
    recommendation: str = ""
    search_metadata: dict[str, Any] = Field(default_factory=dict)


class PolicyEvaluation(BaseModel):
    flight: str
    price: float
    budget_status: str
    approval_required: bool = False
    policy_notes: str = ""
    compliant: bool = True


class PolicyResult(BaseModel):
    policy_evaluation: list[PolicyEvaluation] = Field(default_factory=list)
    auto_approve_eligible: bool = False
    escalation_required: bool = False
    policy_version: str = "v2.3"


class CommsResult(BaseModel):
    channel: str = "slack"
    text: str = ""
    tone_score: str = "empathetic-professional"
    urgency_flag: str = "high"
    slack_ts: str | None = None
    slack_channel: str | None = None


class Resolution(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    event_id: UUID
    status: ResolutionStatus = ResolutionStatus.PROPOSED
    chosen_option: FlightAlternative | None = None
    confidence_score: float = 0.0
    policy_compliant: bool = False
    total_cost_usd: float = 0.0
    total_time_seconds: float = 0.0
    agents_involved: list[str] = Field(default_factory=list)
    research_result: ResearchResult | None = None
    policy_result: PolicyResult | None = None
    comms_result: CommsResult | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

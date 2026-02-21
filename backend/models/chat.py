"""Pydantic models for chat interface."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ChatIntent(StrEnum):
    FLIGHT_DISRUPTION = "flight_disruption"
    CONFIRM = "confirm"
    OPTIONS = "options"
    REJECT = "reject"
    GREETING = "greeting"
    UNKNOWN = "unknown"


class ChatParseResult(BaseModel):
    intent: ChatIntent
    flight_number: str | None = None
    origin: str | None = None
    destination: str | None = None
    disruption_type: str | None = None
    selected_option: int | None = None  # 1-based index when user picks a specific flight
    acknowledgment: str = ""


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    metadata: dict[str, object] = Field(default_factory=dict)


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    image: str | None = None


class ChatStatusResponse(BaseModel):
    status: str  # "processing" | "complete" | "error"
    event_id: str | None = None
    message: ChatMessage | None = None
    resolution: dict[str, object] | None = None

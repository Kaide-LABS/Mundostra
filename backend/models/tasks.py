"""Pydantic models for agent tasks and trace entries."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class AgentName(StrEnum):
    ORCHESTRATOR = "orchestrator"
    RESEARCH = "research"
    POLICY = "policy"
    COMMS = "comms"


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"


class TraceStatus(StrEnum):
    THINKING = "thinking"
    WORKING = "working"
    COMPLETE = "complete"
    ERROR = "error"
    ESCALATION = "escalation"


class AgentTraceEntry(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    event_id: UUID
    agent: AgentName
    model: str = ""
    status: TraceStatus
    message: str
    tokens_used: int = 0
    cost_usd: float = 0.0
    data: dict[str, Any] | None = None


class AgentTask(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    event_id: UUID
    agent: AgentName
    status: TaskStatus = TaskStatus.PENDING
    input_data: dict[str, Any] = Field(default_factory=dict)
    output_data: dict[str, Any] | None = None
    model: str = ""
    tokens_used: int = 0
    cost_usd: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None
    trace: list[AgentTraceEntry] = Field(default_factory=list)

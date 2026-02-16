"""Base agent class — Template Method pattern for all specialist agents."""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from datetime import UTC, datetime
from typing import Any
from uuid import UUID

import httpx

from backend.logging_config import get_logger
from backend.message_bus.bus import MessageBus
from backend.models.tasks import (
    AgentName,
    AgentTask,
    AgentTraceEntry,
    TaskStatus,
    TraceStatus,
)

logger = get_logger(__name__)


class BaseAgent(ABC):
    """Abstract base for all agents.

    Subclasses implement:
    - run() — business logic
    - _call_llm() — SDK-specific LLM invocation
    - _get_mock_response() — canned response for mock_llm mode
    """

    agent_name: AgentName
    model_id: str = ""

    def __init__(
        self,
        bus: MessageBus,
        mock_llm: bool = True,
        base_url: str = "",
        http_transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.bus = bus
        self.mock_llm = mock_llm
        self.base_url = base_url
        self._http_transport = http_transport

    def _make_http_client(self) -> httpx.AsyncClient:
        """Create an httpx client, using injected transport if available."""
        if self._http_transport:
            return httpx.AsyncClient(transport=self._http_transport, base_url=self.base_url)
        return httpx.AsyncClient(base_url=self.base_url)

    async def execute(self, task: AgentTask) -> AgentTask:
        """Public API — handles tracing, timing, and error handling."""
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now(UTC)
        task.model = self.model_id

        await self.emit_trace(
            event_id=task.event_id,
            status=TraceStatus.THINKING,
            message=f"{self.agent_name.value.title()} agent starting...",
        )

        start = time.monotonic()
        try:
            result = await self.run(task)
            task.output_data = result
            task.status = TaskStatus.COMPLETE
            elapsed = time.monotonic() - start

            await self.emit_trace(
                event_id=task.event_id,
                status=TraceStatus.COMPLETE,
                message=f"{self.agent_name.value.title()} agent completed in {elapsed:.1f}s",
                data=result,
                tokens_used=task.tokens_used,
                cost_usd=task.cost_usd,
            )
        except Exception as exc:
            elapsed = time.monotonic() - start
            task.status = TaskStatus.FAILED
            task.output_data = {"error": str(exc)}

            await self.emit_trace(
                event_id=task.event_id,
                status=TraceStatus.ERROR,
                message=f"{self.agent_name.value.title()} agent failed: {exc}",
            )

            await logger.aerror(
                "agent_failed",
                agent=self.agent_name.value,
                error=str(exc),
                elapsed=elapsed,
            )
        finally:
            task.completed_at = datetime.now(UTC)

        return task

    @abstractmethod
    async def run(self, task: AgentTask) -> dict[str, Any]:
        """Agent-specific business logic. Return result dict."""
        ...

    @abstractmethod
    async def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """SDK-specific LLM call. Return raw response text."""
        ...

    @abstractmethod
    def _get_mock_response(self, task: AgentTask) -> dict[str, Any]:
        """Return canned response for mock_llm mode."""
        ...

    async def emit_trace(
        self,
        event_id: UUID,
        status: TraceStatus,
        message: str,
        data: dict[str, Any] | None = None,
        tokens_used: int = 0,
        cost_usd: float = 0.0,
    ) -> None:
        entry = AgentTraceEntry(
            event_id=event_id,
            agent=self.agent_name,
            model=self.model_id,
            status=status,
            message=message,
            data=data,
            tokens_used=tokens_used,
            cost_usd=cost_usd,
        )
        await self.bus.publish(entry)

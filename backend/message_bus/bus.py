"""In-memory async pub/sub message bus for agent trace events."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from collections.abc import Callable, Coroutine
from typing import Any
from uuid import UUID

from backend.logging_config import get_logger
from backend.models.tasks import AgentTraceEntry

logger = get_logger(__name__)

Subscriber = Callable[[AgentTraceEntry], Coroutine[Any, Any, None]]


class MessageBus:
    """Async pub/sub bus for agent trace events.

    Subscribers receive AgentTraceEntry events.
    History is stored per event_id for trace retrieval.
    Failing subscribers never block agents.
    """

    def __init__(self) -> None:
        self._subscribers: list[Subscriber] = []
        self._history: dict[UUID, list[AgentTraceEntry]] = defaultdict(list)

    def subscribe(self, callback: Subscriber) -> None:
        self._subscribers.append(callback)

    async def publish(self, entry: AgentTraceEntry) -> None:
        self._history[entry.event_id].append(entry)

        if not self._subscribers:
            return

        results = await asyncio.gather(
            *(sub(entry) for sub in self._subscribers),
            return_exceptions=True,
        )

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                await logger.awarning(
                    "subscriber_error",
                    subscriber_index=i,
                    error=str(result),
                )

    def get_trace(self, event_id: UUID) -> list[AgentTraceEntry]:
        return list(self._history.get(event_id, []))

    def clear_event(self, event_id: UUID) -> None:
        self._history.pop(event_id, None)

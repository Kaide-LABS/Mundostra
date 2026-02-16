"""WebSocket trace manager — broadcasts agent events to connected clients."""

from __future__ import annotations

from fastapi import WebSocket

from backend.logging_config import get_logger
from backend.message_bus.bus import MessageBus
from backend.models.tasks import AgentTraceEntry

logger = get_logger(__name__)


class TraceManager:
    """Subscribes to MessageBus and broadcasts trace entries to WebSocket clients."""

    def __init__(self, bus: MessageBus) -> None:
        self.bus = bus
        self._connections: list[WebSocket] = []
        bus.subscribe(self._broadcast)

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)
        await logger.ainfo("ws_client_connected", total=len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self._connections:
            self._connections.remove(ws)
        # Log synchronously since disconnect may not be in async context
        logger.info("ws_client_disconnected", total=len(self._connections))

    async def _broadcast(self, entry: AgentTraceEntry) -> None:
        if not self._connections:
            return

        payload = entry.model_dump_json()
        dead: list[WebSocket] = []

        for ws in self._connections:
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)

        for ws in dead:
            self._connections.remove(ws)

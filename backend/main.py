"""FastAPI application entry point."""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from uuid import UUID

import httpx
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.config import get_settings
from backend.logging_config import get_logger, setup_logging
from backend.message_bus.bus import MessageBus
from backend.mock_apis.calendar import router as calendar_router
from backend.mock_apis.cards import router as cards_router
from backend.mock_apis.flights import router as flights_router
from backend.mock_apis.policy import router as policy_router
from backend.models.events import TravelEvent
from backend.models.responses import TravelerResponse
from backend.orchestrator.engine import OrchestratorEngine
from backend.websocket.trace import TraceManager

# Module-level singletons
bus = MessageBus()
engine: OrchestratorEngine = None  # type: ignore[assignment]
trace_manager = TraceManager(bus)

logger = get_logger(__name__)


def _init_engine(http_transport: httpx.AsyncBaseTransport | None = None) -> OrchestratorEngine:
    """Create the orchestrator engine, optionally with a test transport."""
    global engine  # noqa: PLW0603
    engine = OrchestratorEngine(bus, http_transport=http_transport)
    return engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    setup_logging()
    settings = get_settings()

    # Initialize engine with no transport (agents make real HTTP calls in production)
    if engine is None:
        _init_engine()

    await logger.ainfo(
        "startup",
        env=settings.app_env,
        mock_llm=settings.mock_llm,
        port=settings.port,
    )
    yield
    await logger.ainfo("shutdown")


app = FastAPI(
    title="Mundostra Travel OS — Agent Command Center",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS — open for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount mock API routers
app.include_router(flights_router)
app.include_router(calendar_router)
app.include_router(policy_router)
app.include_router(cards_router)


# --- API Endpoints ---


@app.post("/api/events")
async def trigger_event(event: TravelEvent) -> dict[str, object]:
    """Trigger a disruption event and get the resolution."""
    resolution = await engine.handle_event(event)
    return resolution.model_dump(mode="json")


@app.get("/api/events/{event_id}")
async def get_resolution(event_id: UUID) -> dict[str, object]:
    """Get the resolution for a specific event."""
    resolution = engine.get_resolution(event_id)
    if resolution is None:
        return {"error": "Event not found", "event_id": str(event_id)}
    return resolution.model_dump(mode="json")


@app.post("/api/events/{event_id}/respond")
async def respond_to_event(event_id: UUID, response: TravelerResponse) -> dict[str, object]:
    """Handle a traveler response (confirm / options / reject)."""
    resolution = await engine.respond_to_event(str(event_id), response)
    if resolution is None:
        return {"error": "Event not found", "event_id": str(event_id)}
    return resolution.model_dump(mode="json")


@app.post("/api/reset")
async def reset_demo() -> dict[str, str]:
    """Reset all state for a fresh demo run."""
    engine.resolutions.clear()
    bus._history.clear()
    return {"status": "reset"}


@app.get("/api/events/{event_id}/trace")
async def get_trace(event_id: UUID) -> dict[str, object]:
    """Get the full agent trace for an event."""
    entries = bus.get_trace(event_id)
    return {
        "event_id": str(event_id),
        "trace_count": len(entries),
        "trace": [e.model_dump(mode="json") for e in entries],
    }


# --- WebSocket ---


@app.websocket("/ws/trace")
async def websocket_trace(ws: WebSocket) -> None:
    """Real-time trace stream for the dashboard."""
    await trace_manager.connect(ws)
    try:
        while True:
            # Keep connection alive — client sends pings
            await ws.receive_text()
    except WebSocketDisconnect:
        trace_manager.disconnect(ws)


# --- Health ---


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}

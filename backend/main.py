"""FastAPI application entry point."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from backend.chat.parser import ChatParser
from backend.config import get_settings
from backend.logging_config import get_logger, setup_logging
from backend.message_bus.bus import MessageBus
from backend.mock_apis.calendar import router as calendar_router
from backend.mock_apis.cards import router as cards_router
from backend.mock_apis.flights import router as flights_router
from backend.mock_apis.policy import router as policy_router
from backend.models.chat import ChatIntent, ChatRequest
from backend.models.events import (
    EventType,
    FlightDetails,
    PolicyTier,
    TravelerProfile,
    TravelEvent,
)
from backend.models.resolutions import Resolution
from backend.models.responses import TravelerResponse, TravelerResponseType
from backend.orchestrator.engine import OrchestratorEngine
from backend.websocket.trace import TraceManager

# Module-level singletons
bus = MessageBus()
engine: OrchestratorEngine = None  # type: ignore[assignment]
chat_parser: ChatParser = None  # type: ignore[assignment]
trace_manager = TraceManager(bus)

# Chat state: session_id -> event_id mapping, event_id -> resolution result
chat_sessions: dict[str, str] = {}
chat_pending: dict[str, Resolution | None] = {}
chat_events: dict[str, TravelEvent] = {}

# Gathering state: session_id -> context for multi-turn info collection
chat_context: dict[str, dict[str, Any]] = {}

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

    global chat_parser  # noqa: PLW0603

    # Initialize engine with no transport (agents make real HTTP calls in production)
    if engine is None:
        _init_engine()

    # Initialize chat parser
    chat_parser = ChatParser(mock_llm=settings.mock_llm)

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
    engine.events.clear()
    engine.ticket_pdfs.clear()
    bus._history.clear()
    chat_sessions.clear()
    chat_pending.clear()
    chat_events.clear()
    chat_context.clear()
    return {"status": "reset"}


# --- Chat Endpoints ---


def _build_event_from_context(
    ctx: dict[str, Any],
    event_id: UUID,
) -> TravelEvent:
    """Build a TravelEvent from gathered context fields."""
    flight_number = ctx["flight_number"]
    origin = ctx["origin"]
    destination = ctx["destination"]
    disruption = ctx.get("disruption_type") or "cancelled"

    now = datetime.now(UTC)
    departure = now.replace(hour=14, minute=30, second=0, microsecond=0)

    return TravelEvent(
        id=event_id,
        event_type=EventType.FLIGHT_CANCELLED if disruption == "cancelled" else EventType.FLIGHT_DELAYED,
        booking_ref="MUN-CHAT-" + str(event_id)[:8],
        flight=FlightDetails(
            number=flight_number,
            origin=origin,
            destination=destination,
            scheduled_departure=departure,
            status=disruption,
            reason="Reported via chat",
            original_price=400.0,
        ),
        traveler=TravelerProfile(
            name="Chat User",
            email="chat@mundostra.com",
            role="Traveler",
            policy_tier=PolicyTier.EXECUTIVE,
            messaging_id="@chat.user",
        ),
    )


# Required fields and question templates for gathering
_REQUIRED_FIELDS: list[tuple[str, str]] = [
    ("flight_number", "What's your flight number? (e.g., UA 2381)"),
    ("origin", "Which airport are you departing from? (e.g., SFO)"),
    ("destination", "Where are you flying to? (e.g., JFK)"),
]


def _next_missing_question(ctx: dict[str, Any]) -> tuple[str, str] | None:
    """Return (field_name, question) for the next missing required field, or None."""
    for field, question in _REQUIRED_FIELDS:
        if not ctx.get(field):
            return field, question
    return None


def _extract_field_value(field: str, raw: str) -> str | None:
    """Extract a value for the given field from a raw user message."""
    import re

    if field == "flight_number":
        match = re.search(r"\b([A-Z]{2})\s*(\d{1,5})\b", raw, re.IGNORECASE)
        if match:
            return f"{match.group(1).upper()} {match.group(2)}"
        return None
    if field in ("origin", "destination"):
        match = re.search(r"\b([A-Z]{3})\b", raw)
        if match:
            return match.group(1)
        return None
    return raw.strip() or None


async def _run_orchestration(event_id: str, event: TravelEvent) -> None:
    """Background task: run orchestration and store result."""
    try:
        resolution = await engine.handle_event(event)
        chat_pending[event_id] = resolution
    except Exception:
        chat_pending[event_id] = None


def _start_gathering(session_id: str, parse_result: object) -> None:
    """Initialize a gathering context from a parse result."""
    from backend.models.chat import ChatParseResult

    pr: ChatParseResult = parse_result  # type: ignore[assignment]
    chat_context[session_id] = {
        "stage": "gathering",
        "flight_number": pr.flight_number,
        "origin": pr.origin,
        "destination": pr.destination,
        "disruption_type": pr.disruption_type,
        "pending_field": None,
    }


def _fire_orchestration(session_id: str, response: dict[str, object]) -> None:
    """All required fields collected — launch orchestration."""
    ctx = chat_context[session_id]
    ctx["stage"] = "ready"

    event_id = uuid4()
    event_id_str = str(event_id)
    event = _build_event_from_context(ctx, event_id)

    chat_sessions[session_id] = event_id_str
    chat_events[event_id_str] = event

    asyncio.create_task(_run_orchestration(event_id_str, event))

    response["event_id"] = event_id_str
    response["status"] = "processing"


@app.post("/api/chat")
async def chat_message(req: ChatRequest) -> dict[str, object]:
    """Parse a chat message and kick off orchestration if needed."""
    session_id = req.session_id or str(uuid4())
    settings = get_settings()

    # Handle image upload (OCR)
    if req.image:
        from backend.ocr.extractor import extract_from_image

        ocr = await extract_from_image(req.image, mock_llm=settings.mock_llm)
        ocr_resp: dict[str, object] = {
            "session_id": session_id,
            "intent": "flight_disruption",
        }

        if not ocr.success:
            ocr_resp["acknowledgment"] = (
                "I couldn't read that image clearly. Could you type your flight details instead?"
            )
            ocr_resp["status"] = "gathering"
            # Start empty gathering context
            chat_context[session_id] = {
                "stage": "gathering",
                "flight_number": None,
                "origin": None,
                "destination": None,
                "disruption_type": "cancelled",
                "pending_field": "flight_number",
            }
            ack = str(ocr_resp["acknowledgment"])
            ocr_resp["acknowledgment"] = f"{ack} What's your flight number? (e.g., UA 2381)"
            return ocr_resp

        # Populate gathering context from OCR
        chat_context[session_id] = {
            "stage": "gathering",
            "flight_number": ocr.flight_number,
            "origin": ocr.origin,
            "destination": ocr.destination,
            "disruption_type": "cancelled",
            "pending_field": None,
        }
        ocr_ctx = chat_context[session_id]

        missing = _next_missing_question(ocr_ctx)
        if missing:
            next_field, question = missing
            ocr_ctx["pending_field"] = next_field
            found = ", ".join(
                f"**{f}**: {ocr_ctx[f]}"
                for f in ("flight_number", "origin", "destination")
                if ocr_ctx.get(f)
            )
            ocr_resp["acknowledgment"] = (
                f"I read your boarding pass and found: {found}. "
                f"I just need a bit more info. {question}"
            )
            ocr_resp["status"] = "gathering"
        else:
            ocr_resp["acknowledgment"] = (
                f"I read your boarding pass — flight **{ocr_ctx['flight_number']}** from "
                f"**{ocr_ctx['origin']}** to **{ocr_ctx['destination']}**. "
                f"Let me find alternatives for you right away."
            )
            _fire_orchestration(session_id, ocr_resp)
        return ocr_resp

    # If session is in gathering stage, treat message as an answer
    ctx = chat_context.get(session_id)
    if ctx and ctx["stage"] == "gathering" and ctx.get("pending_field"):
        field = ctx["pending_field"]
        value = _extract_field_value(field, req.message)

        response: dict[str, object] = {
            "session_id": session_id,
            "intent": "info_response",
        }

        if value:
            ctx[field] = value
        else:
            # Couldn't parse — re-ask
            _, question = next(
                (f, q) for f, q in _REQUIRED_FIELDS if f == field
            )
            ctx["pending_field"] = field
            response["acknowledgment"] = f"I didn't catch that. {question}"
            response["status"] = "gathering"
            return response

        # Check if more fields needed
        missing = _next_missing_question(ctx)
        if missing:
            next_field, question = missing
            ctx["pending_field"] = next_field
            response["acknowledgment"] = question
            response["status"] = "gathering"
        else:
            response["acknowledgment"] = (
                f"Got it — flight {ctx['flight_number']} from {ctx['origin']} to "
                f"{ctx['destination']}. Let me find alternatives for you right away."
            )
            _fire_orchestration(session_id, response)
        return response

    # Normal intent parsing
    parse_result = await chat_parser.parse(req.message)

    response = {
        "session_id": session_id,
        "intent": parse_result.intent.value,
        "acknowledgment": parse_result.acknowledgment,
    }

    if parse_result.intent == ChatIntent.FLIGHT_DISRUPTION:
        _start_gathering(session_id, parse_result)
        ctx = chat_context[session_id]

        missing = _next_missing_question(ctx)
        if missing:
            # Need more info — enter gathering mode
            next_field, question = missing
            ctx["pending_field"] = next_field
            ack = parse_result.acknowledgment.rstrip(" —-")
            if ack.endswith("let me find alternatives for you right away."):
                ack = ack.replace(
                    " — let me find alternatives for you right away.", "."
                )
            response["acknowledgment"] = f"{ack} I just need a few details first. {question}"
            response["status"] = "gathering"
        else:
            # All details present — fire immediately
            response["acknowledgment"] = parse_result.acknowledgment
            _fire_orchestration(session_id, response)

    elif parse_result.intent in (ChatIntent.CONFIRM, ChatIntent.OPTIONS, ChatIntent.REJECT):
        # Route to existing respond logic
        event_id_str = chat_sessions.get(session_id, "")
        if event_id_str:
            response["event_id"] = event_id_str
            try:
                resp_type = {
                    ChatIntent.CONFIRM: TravelerResponseType.CONFIRM,
                    ChatIntent.OPTIONS: TravelerResponseType.OPTIONS,
                    ChatIntent.REJECT: TravelerResponseType.REJECT,
                }[parse_result.intent]

                resp_obj = TravelerResponse(
                    event_id=event_id_str,
                    response_type=resp_type,
                    selected_option=parse_result.selected_option,
                )
                resolution = await engine.respond_to_event(event_id_str, resp_obj)
                if resolution:
                    response["resolution"] = resolution.model_dump(mode="json")
                    response["status"] = "complete"
                else:
                    response["status"] = "error"
            except Exception:
                response["status"] = "error"
        else:
            response["status"] = "no_active_event"

    return response


@app.get("/api/chat/status/{event_id}")
async def chat_status(event_id: str) -> dict[str, object]:
    """Poll for chat resolution status."""
    if event_id in chat_pending:
        resolution = chat_pending[event_id]
        if resolution is None:
            return {"status": "error", "event_id": event_id}

        return {
            "status": "complete",
            "event_id": event_id,
            "resolution": resolution.model_dump(mode="json"),
        }

    # Still processing
    return {"status": "processing", "event_id": event_id}


@app.get("/api/tickets/{event_id}/pdf")
async def download_ticket_pdf(event_id: str) -> Response:
    """Download the generated ticket PDF for a confirmed booking."""
    pdf_bytes = engine.ticket_pdfs.get(event_id)
    if pdf_bytes is None:
        return Response(content="Ticket not found", status_code=404)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="ticket-{event_id[:8]}.pdf"'},
    )


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

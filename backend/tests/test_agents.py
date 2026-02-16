"""Tests for specialist agents — mock LLM mode."""

from __future__ import annotations

from uuid import uuid4

import pytest

from backend.message_bus.bus import MessageBus
from backend.models.tasks import AgentName, AgentTask, TraceStatus


@pytest.fixture
def agent_bus() -> MessageBus:
    return MessageBus()


class TestResearchAgent:
    @pytest.mark.asyncio
    async def test_mock_response_ranks_by_price(self, agent_bus: MessageBus) -> None:
        from backend.agents.research import ResearchAgent

        agent = ResearchAgent(bus=agent_bus, mock_llm=True, base_url="http://test")
        task = AgentTask(event_id=uuid4(), agent=AgentName.RESEARCH)

        enriched = [
            {
                "flight": "UA105",
                "departure": "2025-02-12T18:30:00",
                "arrival": "2025-02-12T23:45:00",
                "price": 420.0,
                "calendar_conflict": False,
                "conflict_details": None,
                "price_vs_original": "+$20",
                "seat_available": True,
                "source": "mock_inventory_api",
            },
            {
                "flight": "AA210",
                "departure": "2025-02-12T19:15:00",
                "arrival": "2025-02-13T00:15:00",
                "price": 385.0,
                "calendar_conflict": False,
                "conflict_details": None,
                "price_vs_original": "-$15",
                "seat_available": True,
                "source": "mock_inventory_api",
            },
            {
                "flight": "UA900",
                "departure": "2025-02-12T23:00:00",
                "arrival": "2025-02-13T07:30:00",
                "price": 310.0,
                "calendar_conflict": True,
                "conflict_details": "Conflicts with Board Meeting",
                "price_vs_original": "-$90",
                "seat_available": True,
                "source": "mock_inventory_api",
            },
        ]
        result = agent._get_mock_response(task, enriched, 400.0)

        assert "alternatives" in result
        assert "recommendation" in result
        assert len(result["alternatives"]) == 2  # UA900 filtered (calendar conflict)
        # Cheapest no-conflict is AA210 at $385
        assert result["alternatives"][0]["flight"] == "AA210"
        assert task.tokens_used == 1847

    @pytest.mark.asyncio
    async def test_emits_traces(self, agent_bus: MessageBus) -> None:
        from backend.agents.research import ResearchAgent

        agent = ResearchAgent(bus=agent_bus, mock_llm=True, base_url="http://test")

        traces: list[object] = []

        async def _collect(entry: object) -> None:
            traces.append(entry)

        agent_bus.subscribe(_collect)  # type: ignore[arg-type]

        await agent.emit_trace(
            event_id=uuid4(),
            status=TraceStatus.WORKING,
            message="Test trace",
        )
        assert len(traces) == 1


class TestPolicyAgent:
    @pytest.mark.asyncio
    async def test_mock_response(self, agent_bus: MessageBus) -> None:
        from backend.agents.policy import PolicyAgent

        agent = PolicyAgent(bus=agent_bus, mock_llm=True, base_url="http://test")
        task = AgentTask(event_id=uuid4(), agent=AgentName.POLICY)

        result = agent._get_mock_response(task)
        assert "policy_evaluation" in result
        assert result["policy_version"] == "v2.3"
        assert task.tokens_used == 524

    @pytest.mark.asyncio
    async def test_emits_traces(self, agent_bus: MessageBus) -> None:
        from backend.agents.policy import PolicyAgent

        agent = PolicyAgent(bus=agent_bus, mock_llm=True, base_url="http://test")
        traces: list[object] = []

        async def _collect(entry: object) -> None:
            traces.append(entry)

        agent_bus.subscribe(_collect)  # type: ignore[arg-type]

        await agent.emit_trace(event_id=uuid4(), status=TraceStatus.THINKING, message="Test")
        assert len(traces) == 1


class TestCommsAgent:
    @pytest.mark.asyncio
    async def test_mock_response(self, agent_bus: MessageBus) -> None:
        from backend.agents.comms import CommsAgent

        agent = CommsAgent(bus=agent_bus, mock_llm=True, base_url="http://test")
        task = AgentTask(
            event_id=uuid4(),
            agent=AgentName.COMMS,
            input_data={
                "traveler": {"name": "Sarah Chen", "timezone": "America/Los_Angeles"},
                "chosen_option": {"flight": "UA105", "price_vs_original": "+$20"},
                "cancelled_flight": "UA100",
                "origin": "SFO",
                "destination": "JFK",
            },
        )

        result = agent._get_mock_response(task)
        assert result["channel"] == "slack"
        assert "Sarah Chen" in result["text"]
        assert result["tone_score"] == "empathetic-professional"
        assert task.tokens_used == 892

    @pytest.mark.asyncio
    async def test_handles_minimal_input(self, agent_bus: MessageBus) -> None:
        from backend.agents.comms import CommsAgent

        agent = CommsAgent(bus=agent_bus, mock_llm=True, base_url="http://test")
        task = AgentTask(
            event_id=uuid4(),
            agent=AgentName.COMMS,
            input_data={},
        )
        result = agent._get_mock_response(task)
        assert "channel" in result

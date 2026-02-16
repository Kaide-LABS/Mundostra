# Mundostra Travel OS — Project CLAUDE.md

## Project Overview
Multi-Agent Travel OS Support System — demo platform showing autonomous flight disruption resolution using Claude Opus (orchestrator), Claude Haiku (policy), Gemini Flash (research), and GPT-4o (comms).

## Architecture
- **Backend**: FastAPI (Python 3.12+), async, Pydantic models, in-memory message bus
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Framer Motion
- **Real-time**: WebSocket trace streaming from backend to dashboard
- **Agents**: BaseAgent → ResearchAgent, PolicyAgent, CommsAgent, orchestrated by OrchestratorEngine
- **Mock mode**: `MOCK_LLM=true` for deterministic demo without real API keys

## Quality Gates
- **Pre-commit hooks**: ruff lint/format, mypy, ESLint, Prettier
- **CI**: GitHub Actions (`.github/workflows/ci.yml`) — lint, typecheck, test, build
- **Tests**: `pytest backend/tests/` (53 tests), `MOCK_LLM=true` forced in conftest

## Key Commands
```bash
# Backend
source .venv/bin/activate
make test          # pytest
make lint          # ruff check
make typecheck     # mypy
make run           # uvicorn on :8000

# Frontend
make frontend-dev        # next dev on :3000
make frontend-build      # next build
make frontend-lint       # eslint
make frontend-typecheck  # tsc --noEmit
```

## Indexed Nia Resources
- None yet indexed

## Completed Phases
- **Phase 1** (Backend): Multi-agent system, mock APIs, orchestration engine, WebSocket trace
- **Phase 2** (Frontend): Dashboard with EventPanel, AgentStream, Timeline, ConfidenceGauge, CostTicker, ModelUsage, ControlBar
- **Phase 3** (Slack Integration & Polish): Slack Block Kit messages, traveler response flow, reset endpoint, error states, mobile refinements

## Session Handoff — 2026-02-16

### What was done
Phase 3 fully implemented:
- `backend/slack/` package: blocks.py (Block Kit builders), sender.py (SlackSender), app.py (Bolt handlers)
- `backend/models/responses.py`: TravelerResponseType enum, TravelerResponse model
- `backend/orchestrator/engine.py`: `respond_to_event()` method handling confirm/options/reject with card auth, Slack message updates
- `backend/main.py`: POST /api/events/{id}/respond, POST /api/reset, conditional Slack Bolt mount
- `backend/config.py`: slack_bot_token, slack_signing_secret, slack_enabled, slack_default_channel
- `frontend/src/components/SlackPreview.tsx`: Slack-like message bubble
- Frontend: response buttons (Confirm/Options), async reset, status badges (PROPOSED/BOOKED/REJECTED/ESCALATED), error entry styling, mobile polish
- 14 new tests (test_respond, test_reset, test_slack_blocks, test_error_handling)

### Current state
- 53 tests pass
- All quality gates pass (ruff, ESLint, Prettier, tsc, next build)
- Pre-existing mypy errors in logging_config.py, policy.py, research.py (not from Phase 3)
- No git remote configured yet
- Slack integration requires user to create Slack app and set env vars (see .env.example)

### Next steps
- Set up git remote and push initial commit
- Create Slack app (api.slack.com) and configure env vars for live testing
- End-to-end test with ngrok + real Slack workspace
- Consider Phase 4 features (if any planned)

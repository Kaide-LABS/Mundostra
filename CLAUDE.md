# Mundostra Travel OS — Project CLAUDE.md

## Project Overview
Multi-Agent Travel OS Support System — demo platform showing autonomous flight disruption resolution using Claude Opus (orchestrator), Claude Haiku (policy), Gemini 3 Flash Preview (research), and GPT-4o (comms).

## Architecture
- **Backend**: FastAPI (Python 3.12+), async, Pydantic models, in-memory message bus
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Framer Motion
- **Real-time**: WebSocket trace streaming from backend to dashboard
- **Agents**: BaseAgent → ResearchAgent, PolicyAgent, CommsAgent, orchestrated by OrchestratorEngine
- **Messaging**: Microsoft Teams via Incoming Webhook (send-only Adaptive Cards)
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
- **Phase 3** (Teams Integration & Polish): Teams Adaptive Card messages, traveler response flow, reset endpoint, error states, mobile refinements

## Session Handoff — 2026-02-19 (Session 2)

### What was done
Three demo-enhancing changes:
1. **Gemini 3 Flash Preview**: Research model upgraded from `gemini-2.0-flash` to `gemini-3-flash-preview`
2. **Dynamic Dates**: All mock APIs, frontend demo data, and tests now use today's date dynamically — no more hardcoded 2025-02-12 dates
3. **Slack → Microsoft Teams**: Complete migration from Slack (Block Kit + Bolt) to Teams (Adaptive Cards + Incoming Webhook)
   - Created `backend/teams/` package (cards.py, sender.py)
   - Deleted `backend/slack/` (4 files)
   - `slack_id` → `messaging_id` across models/types
   - `SlackPreview` → `TeamsPreview` component (purple #6264A7)
   - Removed `slack-bolt` and `slack-sdk` from dependencies
   - Teams is fire-and-forget (webhook POST, no message updates)

### Current state
- 53 tests pass, frontend builds clean
- `.env` has OpenAI key populated, Teams vars ready (`TEAMS_ENABLED=false`, `TEAMS_WEBHOOK_URL=`)
- `MOCK_LLM=false` in `.env` — ready for real LLM testing once credentials verified
- No git remote configured yet
- Credential files in project root (gitignored): `bedrock-admin_accessKeys.csv`, `service-account.json`

### Credentials status
| Service | Status | What's configured |
|---------|--------|-------------------|
| AWS Bedrock (Opus + Haiku) | Credentials set | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, region `us-east-1` |
| Google Vertex AI (Gemini 3 Flash Preview) | Credentials set | `service-account.json`, `GCP_PROJECT_ID=gen-lang-client-0754692302` |
| OpenAI (GPT-4o) | Credentials set | `OPENAI_API_KEY` in `.env` |
| Microsoft Teams | **Ready to configure** | Set `TEAMS_ENABLED=true` + `TEAMS_WEBHOOK_URL` once webhook created |

### Next steps
- Verify AWS Bedrock model access is enabled for Claude Opus + Haiku in us-east-1
- Verify Gemini 3 Flash Preview is available in Vertex AI us-central1
- Create Teams Incoming Webhook and add URL to `.env`
- Test end-to-end with real LLMs (`MOCK_LLM=false`)
- Set up git remote and push
- Phase 4: pitch collateral (memo, API docs, cost analysis, Cloud Run deploy)

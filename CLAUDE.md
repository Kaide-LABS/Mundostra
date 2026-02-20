# Mundostra Travel OS — Project CLAUDE.md

## Project Overview
Multi-Agent Travel OS Support System — demo platform showing autonomous flight disruption resolution using Claude Opus 4 (orchestrator), Claude 3.5 Haiku (policy), Gemini 2.5 Flash (research), and GPT-4o (comms).

## Architecture
- **Backend**: FastAPI (Python 3.12+), async, Pydantic models, in-memory message bus
- **Frontend**: Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, Framer Motion
- **Real-time**: WebSocket trace streaming from backend to dashboard
- **Agents**: BaseAgent → ResearchAgent, PolicyAgent, CommsAgent, orchestrated by OrchestratorEngine
- **Messaging**: Gmail via SMTP (send-only HTML emails with App Password)
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
- **Phase 3** (Messaging & Polish): Gmail HTML email messages (replaced Discord), traveler response flow, reset endpoint, error states, mobile refinements

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
- Create Teams Incoming Webhook and add URL to `.env`
- Phase 4: pitch collateral (memo, API docs, cost analysis, Cloud Run deploy)

## Session Handoff — 2026-02-20 (Session 3)

### What was done
1. **Orchestrator model → Claude Opus 4**: Changed `orchestrator_model_id` from `us.anthropic.claude-sonnet-4-20250514-v1:0` to `us.anthropic.claude-opus-4-20250514-v1:0`
2. **Research model → Gemini 2.5 Flash**: `gemini-3-flash-preview` was not available on the Vertex AI project; switched to `gemini-2.5-flash` which is the latest accessible model
3. **Fixed GCP credentials propagation**: Added `google_application_credentials` field to Settings and auto-export to `os.environ` on startup so Vertex AI SDK picks it up from `.env`
4. **Verified all 4 LLM credentials**: AWS Bedrock (Opus + Haiku), Vertex AI (Gemini 2.5 Flash), OpenAI (GPT-4o) — all confirmed working
5. **Successful E2E test with real LLMs**: Full flight cancellation scenario — orchestrator coordinated research (6 alternatives found), policy (auto-approve eligible), comms (empathetic message generated). Confidence 0.94, cost $0.014, ~83s total
6. **Pushed to GitHub**: Private repo `Mundostra` created, all code pushed

### Current state
- All 53 tests pass, real LLM E2E verified
- GitHub remote configured and code pushed
- `MOCK_LLM=false` in `.env` for real LLM mode

### Credentials status
| Service | Status | Verified |
|---------|--------|----------|
| AWS Bedrock (Opus 4 + Haiku 3.5) | Working | 2026-02-20 |
| Google Vertex AI (Gemini 2.5 Flash) | Working | 2026-02-20 |
| OpenAI (GPT-4o) | Working | 2026-02-20 |
| Discord | Not yet configured | — |

### Next steps
- Phase 4: pitch collateral (memo, API docs, cost analysis, Cloud Run deploy)

## Session Handoff — 2026-02-20 (Session 4)

### What was done
**Discord → Gmail (SMTP)**: Complete migration from Discord webhooks to Gmail SMTP emails.
- Created `backend/gmail/` package (`emails.py`, `sender.py`, `__init__.py`)
- `emails.py`: 3 HTML email builders with inline CSS (`build_resolution_email`, `build_confirmation_email`, `build_options_email`)
- `sender.py`: `GmailSender` class using `aiosmtplib` (smtp.gmail.com:587, STARTTLS, App Password)
- Deleted `backend/discord_integration/` (embeds.py, sender.py, __init__.py)
- Updated `backend/config.py`: `discord_enabled`/`discord_webhook_url` → `gmail_enabled`/`gmail_sender`/`gmail_app_password`/`gmail_recipient`
- Updated `backend/models/resolutions.py`: `CommsResult.channel="email"`, `discord_sent` → `email_sent`
- Updated `backend/agents/comms.py`: `discord_sender` → `gmail_sender`, `_send_discord()` → `_send_email()`
- Updated `backend/orchestrator/engine.py`: `DiscordSender` → `GmailSender`, builds email dicts instead of embeds
- Updated `backend/orchestrator/prompts.py`: "Discord" → "email" in comms system prompt
- Created `frontend/src/components/EmailPreview.tsx` (Gmail red #EA4335, envelope icon)
- Deleted `frontend/src/components/DiscordPreview.tsx`
- Updated `frontend/src/components/EventPanel.tsx`: uses `EmailPreview`, reads `email_sent`
- Updated `frontend/src/types/api.ts`: `discord_sent` → `email_sent`
- Created `backend/tests/test_gmail_emails.py`, updated `test_e2e.py` and `test_agents.py`
- Added `aiosmtplib>=3.0.0` to `pyproject.toml`
- Updated `.env`: Discord vars → Gmail vars

### Current state
- All 53 tests pass, frontend builds clean
- Gmail integration ready to configure: set `GMAIL_ENABLED=true`, `GMAIL_SENDER`, `GMAIL_APP_PASSWORD`, `GMAIL_RECIPIENT`
- Gmail requires a Google App Password (not regular password)

### Credentials status
| Service | Status | Verified |
|---------|--------|----------|
| AWS Bedrock (Opus 4 + Haiku 3.5) | Working | 2026-02-20 |
| Google Vertex AI (Gemini 2.5 Flash) | Working | 2026-02-20 |
| OpenAI (GPT-4o) | Working | 2026-02-20 |
| Gmail (SMTP) | **Ready to configure** | Set `GMAIL_ENABLED=true` + credentials |

### Next steps
- Configure Gmail App Password and add to `.env`
- Phase 4: pitch collateral (memo, API docs, cost analysis, Cloud Run deploy)

## Session Handoff — 2026-02-20 (Session 5)

### What was done
1. **Cloud Run Deployment Config**: Created `Dockerfile.backend` (Python 3.12 slim), `Dockerfile.frontend` (3-stage Node 20 Alpine with standalone output), `.dockerignore`, and `deploy.sh` (one-command gcloud deploy script)
2. **backend/config.py**: Made `base_url` dynamic via `model_post_init` (defaults from `self.port`); skips `GOOGLE_APPLICATION_CREDENTIALS` export when empty (Cloud Run uses metadata server)
3. **frontend/next.config.js**: Added `output: 'standalone'` for Docker-optimized builds
4. **Committed all pending work**: Chat UI, admin page, Amadeus flight search, backend chat module — 26 files, 1899 insertions
5. **Deployed to Cloud Run**: Backend (`mundostra-api`) and frontend (`mundostra-web`) deployed via Cloud Shell using `deploy.sh`
6. **Demo video script**: Drafted a pitch demo script tailored for Vinuta Chopra (CEO) based on CONTEXT.MD founder profiling

### Deployment details
- **GCP Project**: `gen-lang-client-0754692302`, region `us-central1`
- **Backend service**: `mundostra-api` — Cloud Run, 1Gi memory, port 8000, env vars from `.env`
- **Frontend service**: `mundostra-web` — Cloud Run, 512Mi memory, port 3000, `NEXT_PUBLIC_API_URL` baked at build time
- **Cloud Build**: Uses `/tmp/cloudbuild-*.yaml` temp configs to specify custom Dockerfiles
- **No `GOOGLE_APPLICATION_CREDENTIALS`** on Cloud Run — service account handles Vertex AI auth
- **Important**: Cloud Run compute service account needs `roles/aiplatform.user` for Vertex AI

### Files created
- `Dockerfile.backend` — Python 3.12 slim, installs from pyproject.toml, runs uvicorn
- `Dockerfile.frontend` — 3-stage (deps → build → run), standalone Next.js output
- `.dockerignore` — excludes secrets, caches, .git, node_modules
- `deploy.sh` — sources .env, builds via Cloud Build, deploys both services, prints URLs

### Current state
- 81 tests pass, frontend builds clean
- All code pushed to GitHub (`Kaide-LABS/Mundostra`)
- Cloud Run services deployed (may need redeploy after chat UI commit was pushed)

### Next steps
- Verify Cloud Run deployment has latest chat UI (run `git pull && ./deploy.sh` in Cloud Shell)
- Grant Vertex AI User role to Cloud Run service account if not done
- Record demo video using the script drafted this session
- Phase 4 remaining: memo, API docs, cost analysis

## Future Enhancements (Nice-to-Haves)
- **Ticket Image OCR**: Allow users to upload a photo of their boarding pass/ticket in chat. Use Gemini vision to extract flight number, origin, destination — skipping the text gathering flow.
- **Auto-Generated Ticket PDF**: After booking is confirmed, automatically generate a downloadable ticket/boarding pass file with the new flight details.

# Product Requirements Document (PRD)
# Mundostra Pitch Demo: Multi-Agent Travel OS Support System

**Version:** 0.2 (Decisions Applied)
**Author:** [Your Name]
**Date:** 2026-02-11
**Status:** Ready for Phase 1 Execution

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Problem Statement](#2-problem-statement)
3. [Target Audience & Personas](#3-target-audience--personas)
4. [Product Vision](#4-product-vision)
5. [Architecture Overview](#5-architecture-overview)
6. [Agent Specifications](#6-agent-specifications)
7. [Dashboard Specification](#7-dashboard-specification)
8. [Demo Scenario: End-to-End Flow](#8-demo-scenario-end-to-end-flow)
9. [Data Models & API Contracts](#9-data-models--api-contracts)
10. [Technical Stack](#10-technical-stack)
11. [Phased Delivery Plan](#11-phased-delivery-plan)
12. [Success Criteria](#12-success-criteria)
13. [Risks & Mitigations](#13-risks--mitigations)
14. [Open Questions](#14-open-questions)

---

## 1. Executive Summary

### What We're Building

A **live, working multi-agent demo** that solves Mundostra's most painful operational problem — support latency for disrupted travelers — using a coordinated system of AI agents powered by Claude, Gemini, and OpenAI.

### Why It Matters

This demo serves a dual purpose:

1. **For Mundostra:** It delivers a functional prototype of their "Self-Healing Support Agent" — the missing piece that lets their small team compete with Navan's thousands of support staff.
2. **For our pitch:** The multi-agent architecture that powers the demo IS the proof of our AI-enhanced development sprint methodology. The process is the product.

### The "Stupid to Say No" Proposition

Mundostra is in Design Partner phase with ~10 early clients. They need to deliver enterprise-grade service with a skeleton crew. We hand them a working system that autonomously resolves flight disruptions in under 60 seconds — and show them the agent framework can be extended to expenses, card pre-checks, and policy enforcement in subsequent sprints.

---

## 2. Problem Statement

### Mundostra's Core Tension

Mundostra operates a "No Markup" business model. Unlike Navan or TravelPerk, they don't hide margin in inflated booking prices. This means:

- **Every human support interaction is a direct cost** with no hidden revenue to offset it
- They cannot afford a call center
- Yet their Design Partners expect instant, reliable support when travel goes wrong

### The Specific Pain Points (from founder's own Reddit posts)

| Pain Point | Impact | Current State |
|---|---|---|
| **Support latency** | 3+ hour waits for disruption resolution | Manual triage by small team |
| **Virtual card failures** | Travelers stranded at hotel check-in at 1 AM | Reactive — fix after the fact |
| **Price transparency** | CFOs don't trust the "no markup" claim without proof | No automated audit trail |

### What They Need

An **asymmetric technology** that lets 1 person handle what normally requires 50. Not a chatbot — an autonomous agent system that detects, decides, and resolves.

---

## 3. Target Audience & Personas

### Primary: Vinuta Chopra (CEO / Product)

| Attribute | Detail |
|---|---|
| Background | Amazon (Sr. PM Technical), Expedia |
| Decision style | Data-driven, skeptical, written-culture |
| Buying trigger | "Does this improve our margins and NPS?" |
| Wants to see | ROI metrics, admin dashboard, written memo with numbers |
| Language that works | "Reduces TRT by 42%", "Saves $X per resolution" |
| Language that fails | "Cutting-edge AI", "Revolutionary platform" |

### Secondary: Piyush Awasthi (Tech Co-founder)

| Attribute | Detail |
|---|---|
| Background | Indie hacker, SaaS community, code-first |
| Decision style | "Show me the repo", anti-enterprise-sales |
| Buying trigger | "Does this save me 100 hours of coding?" |
| Wants to see | API docs, JSON payloads, sandbox, GitHub repo |
| Language that works | "Here's the curl command", "Drop this webhook in" |
| Language that fails | "Schedule a follow-up", "Let's align on synergies" |

### Tertiary: Mundostra's Design Partners (the 10 early clients)

They don't see the demo directly, but the demo must be something Mundostra can **show** to these partners as a native capability. The dashboard should feel like it belongs in the Travel OS.

---

## 4. Product Vision

### The Dual-Purpose Demo

```
┌──────────────────────────────────────────────────────┐
│                    THE DEMO                           │
│                                                      │
│  ┌─────────────────┐    ┌─────────────────────────┐  │
│  │  WHAT MUNDOSTRA │    │  WHAT MUNDOSTRA SEES    │  │
│  │  GETS           │    │  ABOUT US               │  │
│  │                 │    │                         │  │
│  │  A working      │    │  A multi-agent AI       │  │
│  │  self-healing   │    │  development team that  │  │
│  │  support agent  │    │  ships production-grade │  │
│  │  system         │    │  systems in sprints     │  │
│  └─────────────────┘    └─────────────────────────┘  │
└──────────────────────────────────────────────────────┘
```

### Core Principle: The Architecture IS the Demo

The multi-agent orchestration pattern we use to BUILD the system is the same pattern that RUNS the system. This is not a coincidence — it's the thesis of the pitch. AI-enhanced sprints produce AI-enhanced products.

---

## 5. Architecture Overview

### 5.1 High-Level System Architecture

```
                    ┌──────────────┐
                    │   EVENT      │
                    │   SOURCE     │
                    │ (Webhook /   │
                    │  Trigger)    │
                    └──────┬───────┘
                           │
                           ▼
                ┌──────────────────┐
                │   ORCHESTRATOR   │
                │  (Claude Opus)   │
                │                  │
                │  • Event intake  │
                │  • Task planning │
                │  • Agent dispatch│
                │  • Result merge  │
                │  • Decision gate │
                └──┬───────┬───┬──┘
                   │       │   │
          ┌────────┘       │   └────────┐
          ▼                ▼            ▼
   ┌─────────────┐ ┌────────────┐ ┌─────────────┐
   │   RESEARCH  │ │   POLICY   │ │    COMMS     │
   │   AGENT     │ │   AGENT    │ │    AGENT     │
   │  (Gemini)   │ │  (Claude)  │ │  (OpenAI)   │
   │             │ │            │ │             │
   │ • Find alt  │ │ • Budget   │ │ • Draft msg │
   │   flights   │ │   check    │ │ • Tone/     │
   │ • Calendar  │ │ • Policy   │ │   empathy   │
   │   conflicts │ │   rules    │ │ • Channel   │
   │ • Price     │ │ • Approval │ │   routing   │
   │   comparison│ │   chain    │ │ • Escalation│
   └──────┬──────┘ └─────┬──────┘ └──────┬──────┘
          │              │               │
          └──────────┬───┘───────────────┘
                     ▼
          ┌──────────────────┐
          │   ACTION LAYER   │
          │                  │
          │ • Slack notify   │
          │ • Card adjust    │
          │ • Booking confirm│
          │ • Audit log      │
          └──────────────────┘
                     │
                     ▼
          ┌──────────────────┐
          │  LIVE DASHBOARD  │
          │  (WebSocket)     │
          │                  │
          │ • Agent activity │
          │ • Decision trace │
          │ • Cost tracking  │
          │ • Timeline view  │
          └──────────────────┘
```

### 5.2 Why Three Different Models?

This is not arbitrary. Each model is chosen for a specific strength:

| Agent | Model | Rationale |
|---|---|---|
| **Orchestrator** | Claude Opus 4.5 (via AWS Bedrock) | Best at complex reasoning, multi-step planning, and maintaining coherent state across a long decision chain |
| **Research Agent** | Gemini 3 Flash (via Vertex AI) | Strong at rapid information synthesis, large context windows for comparing multiple flight options simultaneously |
| **Policy Agent** | Claude Haiku (latest, via AWS Bedrock) | Excellent at rule-following, structured logic, and compliance checking — lower cost than Opus for constrained tasks |
| **Comms Agent** | OpenAI GPT-5.2 | Strong at natural, empathetic language generation — the traveler-facing message needs warmth, not precision |

This multi-model approach also demonstrates **vendor independence** — a key selling point for Vinuta's Amazon-trained risk management mindset.

### 5.3 Communication Pattern

Agents communicate via a **message bus** (in-memory for the demo, replaceable with Redis/NATS in production):

```
Event → Orchestrator → [parallel dispatch] → Agents → Results → Orchestrator → Decision → Action
```

All agent messages are logged to a **trace stream** consumed by the dashboard via WebSocket. This makes the "thinking" visible.

---

## 6. Agent Specifications

### 6.1 Orchestrator Agent (Claude Opus 4.5 via AWS Bedrock)

**Model:** Claude Opus 4.5 via AWS Bedrock
**Role:** The "brain" — receives events, decomposes them into tasks, dispatches to specialist agents, merges results, makes final decisions.

**Inputs:**
- Event payload (flight cancellation, card failure, etc.)
- Traveler profile (name, preferences, loyalty numbers, calendar)
- Company policy document (budget caps, approval rules)

**Outputs:**
- Task assignments to specialist agents
- Final resolution decision
- Audit trail entry

**Behavior Rules:**
- MUST dispatch Research and Policy agents in parallel (not sequential)
- MUST wait for both before dispatching Comms agent (comms needs the data)
- MUST include confidence score (0-1) in final decision
- If confidence < 0.7, escalate to human (HITL — Human in the Loop)
- MUST log every decision with reasoning (for the dashboard trace)

**System Prompt Structure:**
```
You are the Orchestrator of a travel support system.
You receive disruption events and coordinate specialist agents to resolve them.

Your decision framework:
1. ASSESS: What happened? Who is affected? What is the urgency?
2. DISPATCH: Send parallel tasks to Research Agent and Policy Agent.
3. SYNTHESIZE: Merge their findings into a resolution plan.
4. DECIDE: Choose the best option. Assign a confidence score.
5. ACT: If confidence >= 0.7, dispatch Comms Agent. If < 0.7, escalate.

You must output structured JSON at every step.
```

### 6.2 Research Agent (Gemini 3 Flash via Vertex AI)

**Model:** Gemini 3 Flash via Google Vertex AI
**Role:** Information gatherer — finds alternative flights, checks calendar conflicts, compares prices.

**Inputs (from Orchestrator):**
- Cancelled flight details (route, time, airline, booking ref)
- Traveler's calendar window (next 12 hours)
- Price constraints (from policy)

**Outputs:**
```json
{
  "alternatives": [
    {
      "flight": "UA105",
      "departure": "2025-02-12T18:30:00Z",
      "arrival": "2025-02-12T21:45:00Z",
      "price": 420,
      "calendar_conflict": false,
      "conflict_details": null,
      "price_vs_original": "+$20",
      "seat_available": true,
      "source": "mock_inventory_api"
    }
  ],
  "recommendation": "UA105 — cheapest, no conflicts, departs in 2 hours",
  "search_metadata": {
    "options_evaluated": 7,
    "options_filtered_by_policy": 3,
    "options_filtered_by_calendar": 1
  }
}
```

**Behavior Rules:**
- Search a minimum of 3 alternative options
- Flag any option that exceeds the policy budget cap
- Check calendar for each viable option
- Rank by: (1) calendar fit, (2) price, (3) departure proximity

### 6.3 Policy Agent (Claude Haiku via AWS Bedrock)

**Model:** Claude Haiku (latest) via AWS Bedrock
**Role:** Compliance checker — validates that proposed resolutions comply with the traveler's company policy.

**Inputs (from Orchestrator):**
- Proposed flight alternatives (from Research Agent, relayed by Orchestrator)
- Company travel policy document
- Traveler's role/level (affects approval thresholds)
- Original booking cost

**Outputs:**
```json
{
  "policy_evaluation": [
    {
      "flight": "UA105",
      "price": 420,
      "budget_status": "within_cap",
      "approval_required": false,
      "policy_notes": "Price delta +$20 is under auto-approve threshold of $50",
      "compliant": true
    }
  ],
  "auto_approve_eligible": true,
  "escalation_required": false,
  "policy_version": "v2.3"
}
```

**Behavior Rules:**
- NEVER approve a booking that exceeds the hard budget cap without escalation
- Apply role-based rules (e.g., VP gets higher thresholds than IC)
- If multiple options are compliant, don't pick — return all with flags
- Include the specific policy clause that justifies each decision

### 6.4 Communications Agent (OpenAI GPT-5.2)

**Model:** OpenAI GPT-5.2
**Role:** Traveler-facing message crafter — writes the Slack/email notification with empathy, clarity, and actionable options.

**Inputs (from Orchestrator, after synthesis):**
- Chosen resolution (or options for traveler to pick)
- Traveler's name and context (time zone, current location)
- Urgency level
- Channel preference (Slack, email, SMS)

**Outputs:**
```json
{
  "message": {
    "channel": "slack",
    "text": "Hi Sarah — your flight UA100 (SFO→JFK) has been cancelled. I've found you a seat on UA105, departing at 6:30 PM — gets you in by 9:45 PM, no conflict with your 10 AM meeting tomorrow. The cost difference is +$20, auto-approved under company policy. Reply *confirm* to book, or *options* to see alternatives.",
    "blocks": [...],
    "tone_score": "empathetic-professional",
    "urgency_flag": "high"
  },
  "escalation_message": null
}
```

**Behavior Rules:**
- Lead with the problem, immediately follow with the solution
- Include specific times in the traveler's local time zone
- Always give the traveler a choice (confirm vs. see alternatives)
- Keep messages under 100 words for Slack
- Never use jargon ("PNR", "GDS", "fare class")

---

## 7. Dashboard Specification

### 7.1 Purpose

The dashboard is the **visual centerpiece** of the pitch. It serves three functions:

1. **Demo theater:** Watch agents think, coordinate, and resolve in real-time
2. **Operational tool:** Something Mundostra could ship to admins managing their Design Partners
3. **Proof of methodology:** The visible agent orchestration proves the multi-agent sprint approach works

### 7.2 Layout

```
┌─────────────────────────────────────────────────────────────┐
│  MUNDOSTRA TRAVEL OS — Agent Command Center                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────┐  ┌──────────────────────────────┐  │
│  │   EVENT PANEL       │  │   AGENT ACTIVITY STREAM      │  │
│  │                     │  │                              │  │
│  │  [!] Flight UA100   │  │  ● Orchestrator: Event       │  │
│  │  SFO → JFK          │  │    received. Classifying...  │  │
│  │  CANCELLED           │  │  ● Orchestrator: Dispatching │  │
│  │                     │  │    Research + Policy agents   │  │
│  │  Traveler:          │  │  ● Research (Gemini): Querying│  │
│  │  Sarah Chen         │  │    7 alternative flights...  │  │
│  │  VP Engineering     │  │  ● Policy (Claude): Checking │  │
│  │                     │  │    budget cap for VP role... │  │
│  │  Policy: VP-Tier    │  │  ● Research: Found 3 viable  │  │
│  │  Budget Cap: $800   │  │    options. Best: UA105 $420 │  │
│  │                     │  │  ● Policy: UA105 approved.   │  │
│  │                     │  │    Under auto-approve limit. │  │
│  │                     │  │  ● Orchestrator: Confidence   │  │
│  │                     │  │    0.94. Dispatching Comms.  │  │
│  │                     │  │  ● Comms (OpenAI): Drafting  │  │
│  │                     │  │    Slack notification...     │  │
│  │                     │  │  ✓ RESOLVED — 34 seconds     │  │
│  └─────────────────────┘  └──────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  RESOLUTION TIMELINE                                    │ │
│  │                                                         │ │
│  │  0s        8s       15s       22s       30s      34s    │ │
│  │  ├─────────┼─────────┼─────────┼─────────┼────────┤    │ │
│  │  Event   Research  Policy   Synthesis  Comms   Done     │ │
│  │  ●━━━━━━━●━━━━━━━━━●━━━━━━━━●━━━━━━━━━●━━━━━━━●        │ │
│  │          └──parallel──┘                                 │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │  COST         │  │  CONFIDENCE  │  │  MODEL USAGE        │  │
│  │  $0.037       │  │  0.94 / 1.0  │  │  Opus 4.5: 1 call  │  │
│  │  total API    │  │  ████████░░  │  │  Gemini 3: 1 call  │  │
│  │  cost for     │  │              │  │  Haiku: 1 call     │  │
│  │  resolution   │  │  Auto-approve│  │  GPT-5.2: 1 call   │  │
│  └──────────────┘  └──────────────┘  └───────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │  [  Trigger Demo Event  ]    [ Reset ]    [ Settings ] │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 Key Dashboard Elements

| Element | What It Shows | Why It Matters |
|---|---|---|
| **Event Panel** | The disruption details + traveler profile | Sets the scene — this is a real person with a real problem |
| **Agent Activity Stream** | Real-time log of each agent's actions and decisions | The "wow factor" — watching AI agents coordinate live |
| **Resolution Timeline** | Horizontal timeline showing parallel agent execution | Proves agents run concurrently, not sequentially — shows speed |
| **Cost Ticker** | Total API cost for this resolution | Kills the "AI is expensive" objection. ~$0.03 per resolution vs. $25+ for a human agent |
| **Confidence Score** | Orchestrator's confidence in the decision | Demonstrates HITL safety — low confidence = human escalation |
| **Model Usage** | Which models were called and how many times | Proves the multi-model architecture — no single vendor dependency |
| **Trigger Button** | Big button to fire a demo event | Lets Piyush click it himself — interactive demo, not a slideshow |
| **JSON Inspector Panel** | Collapsible raw JSON view per agent (input/output payloads) | Piyush can click any agent step to see the actual JSON — proves nothing is faked, shows the real API contract |

### 7.4 Real-Time Data Flow

```
Backend (Python) → WebSocket → Frontend (Next.js)

Each agent emits events:
{
  "timestamp": "2025-02-12T18:00:01.234Z",
  "agent": "research",
  "model": "gemini-3-flash",
  "status": "working",
  "message": "Querying 7 alternative flights...",
  "tokens_used": 0,
  "cost": 0.00
}

On completion:
{
  "timestamp": "2025-02-12T18:00:08.567Z",
  "agent": "research",
  "model": "gemini-3-flash",
  "status": "complete",
  "message": "Found 3 viable options. Best: UA105 at $420",
  "tokens_used": 1847,
  "cost": 0.0092
}
```

---

## 8. Demo Scenario: End-to-End Flow

### The Story

> Sarah Chen, VP of Engineering at a Mundostra Design Partner company, is at SFO airport. Her 4:00 PM flight to JFK (UA100) just got cancelled. She has a 10:00 AM board meeting in Manhattan tomorrow. It's now 3:45 PM Pacific.

### Step-by-Step Flow

#### Step 1: Event Trigger
- **Source:** Mock webhook (simulating FlightAware / airline notification)
- **Payload:**
```json
{
  "event_type": "flight_cancelled",
  "booking_ref": "MND-2025-00847",
  "flight": {
    "number": "UA100",
    "origin": "SFO",
    "destination": "JFK",
    "scheduled_departure": "2025-02-12T16:00:00-08:00",
    "status": "cancelled",
    "reason": "mechanical"
  },
  "traveler": {
    "name": "Sarah Chen",
    "email": "sarah@designpartner.com",
    "role": "VP Engineering",
    "policy_tier": "executive",
    "slack_id": "U0123SARAH",
    "calendar_integration": true,
    "timezone": "America/Los_Angeles"
  }
}
```

#### Step 2: Orchestrator Receives & Plans (0-3 seconds)
- Claude Opus 4.5 reads the event
- Classifies: **disruption / flight / cancellation / high-urgency**
- Creates task plan:
  - Task A (Research Agent): Find alternative flights SFO→JFK, next 8 hours
  - Task B (Policy Agent): Retrieve policy for "executive" tier, determine budget cap and auto-approve threshold
- Dispatches Task A and Task B **in parallel**

#### Step 3: Research Agent Executes (3-12 seconds)
- Gemini queries mock flight inventory API
- Returns 7 options
- Checks traveler's calendar (mock Google Calendar API) for each
- Filters to 3 viable options:
  - UA105: Departs 6:30 PM, $420, no calendar conflict
  - AA210: Departs 7:15 PM, $385, no calendar conflict
  - UA900: Departs 9:00 PM (redeye), $310, no conflict but arrives 5:30 AM

#### Step 4: Policy Agent Executes (3-10 seconds, parallel with Step 3)
- Claude Haiku reads the company's travel policy JSON
- Executive tier: budget cap $800, auto-approve delta up to $100
- Original booking was $400
- All three options are under cap and under auto-approve threshold

#### Step 5: Orchestrator Synthesizes (12-18 seconds)
- Receives results from both agents
- Merges: Research found 3 options, all policy-compliant
- Ranks by composite score: UA105 wins (best time/price/calendar balance)
- Confidence: 0.94 (high — clear winner, all checks pass)
- Dispatches Comms Agent with the resolution

#### Step 6: Comms Agent Drafts Message (18-25 seconds)
- OpenAI GPT-5.2 generates the Slack message
- Considers: tone (empathetic — she's stranded), urgency (high), context (has a morning meeting)
- Produces the message and Slack Block Kit JSON

#### Step 7: Action Layer Executes (25-34 seconds)
- Slack message sent to Sarah
- Virtual card authorization updated for UA105 price
- Audit log entry written
- Dashboard shows: **RESOLVED — 34 seconds**

#### Step 8: Traveler Interaction
- Sarah sees the Slack message
- Replies "confirm"
- System books UA105, sends confirmation with boarding pass link
- Dashboard updates: **BOOKED**

---

## 9. Data Models & API Contracts

### 9.1 Core Data Models

#### Event
```typescript
interface TravelEvent {
  id: string;
  event_type: "flight_cancelled" | "flight_delayed" | "card_declined" | "hotel_overbooked";
  timestamp: string;           // ISO 8601
  booking_ref: string;
  flight?: FlightDetails;
  hotel?: HotelDetails;
  traveler: TravelerProfile;
  metadata: Record<string, any>;
}
```

#### Traveler Profile
```typescript
interface TravelerProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  policy_tier: "standard" | "manager" | "executive";
  slack_id: string;
  timezone: string;
  preferences: {
    airline_loyalty: string[];
    seat_preference: "window" | "aisle" | "no_preference";
    meal_preference: string;
  };
  calendar_integration: boolean;
}
```

#### Agent Task
```typescript
interface AgentTask {
  id: string;
  agent: "research" | "policy" | "comms";
  status: "pending" | "running" | "complete" | "failed";
  input: Record<string, any>;
  output: Record<string, any> | null;
  model: string;
  tokens_used: number;
  cost_usd: number;
  started_at: string;
  completed_at: string | null;
  trace: AgentTraceEntry[];     // For the dashboard stream
}
```

#### Agent Trace Entry (for dashboard streaming)
```typescript
interface AgentTraceEntry {
  timestamp: string;
  agent: string;
  model: string;
  status: "thinking" | "working" | "complete" | "error" | "escalation";
  message: string;              // Human-readable status
  tokens_used: number;
  cost_usd: number;
  data?: Record<string, any>;   // Optional structured data
}
```

#### Resolution
```typescript
interface Resolution {
  id: string;
  event_id: string;
  status: "proposed" | "confirmed" | "rejected" | "escalated";
  chosen_option: FlightAlternative;
  confidence_score: number;      // 0.0 - 1.0
  policy_compliant: boolean;
  total_cost_usd: number;        // API cost to resolve
  total_time_seconds: number;
  agents_involved: string[];
  audit_trail: AgentTraceEntry[];
}
```

### 9.2 Internal API Endpoints (Backend)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/events` | Receive/trigger a disruption event |
| GET | `/api/events/:id` | Get event status and resolution |
| GET | `/api/events/:id/trace` | Get full agent trace for event |
| WS | `/ws/trace` | WebSocket stream for real-time dashboard |
| POST | `/api/events/:id/respond` | Traveler response (confirm/reject) |
| GET | `/api/dashboard/stats` | Aggregate stats (avg resolution time, cost, etc.) |

### 9.3 Mock External APIs

These simulate the integrations Mundostra would have in production:

| Mock API | Simulates | Endpoint |
|---|---|---|
| Flight Inventory | Amadeus / Duffel | `/mock/flights/search` |
| Calendar | Google Calendar API | `/mock/calendar/check` |
| Travel Policy | Mundostra's policy engine | `/mock/policy/evaluate` |
| Virtual Card | Stripe Issuing / Marqeta | `/mock/cards/authorize` |
| Slack | Slack Bot API | `/mock/slack/send` (or real Slack in full demo) |

---

## 10. Technical Stack

### 10.1 Backend

| Component | Technology | Rationale |
|---|---|---|
| Runtime | **Python 3.12+** | AI/ML ecosystem, fast prototyping, async support |
| Framework | **FastAPI** | Async-native, WebSocket support, auto-generated API docs (Piyush will appreciate the Swagger UI) |
| Agent Orchestration | **Custom lightweight framework** | No heavy framework dependencies — keeps it understandable and demo-friendly |
| AI SDKs | `boto3` (Bedrock), `google-cloud-aiplatform` (Vertex AI), `openai` | AWS Bedrock for Claude models, Vertex AI for Gemini, OpenAI direct for GPT-5.2 |
| WebSocket | **FastAPI WebSocket** | Native support, streams trace events to dashboard |
| Task Execution | **asyncio** | Parallel agent dispatch without threading complexity |

### 10.2 Frontend (Dashboard)

| Component | Technology | Rationale |
|---|---|---|
| Framework | **Next.js 14 (App Router)** | Aligns with Mundostra's likely stack, SSR for fast initial load |
| Styling | **Tailwind CSS** | Rapid UI development, clean aesthetic |
| Real-time | **Native WebSocket** | Direct connection to FastAPI backend |
| Animations | **Framer Motion** | Smooth agent activity animations (trace entries appearing, timeline animating) |
| Charts | **Lightweight (custom SVGs or recharts)** | For the cost ticker and confidence gauge — no heavy charting library |

### 10.3 Infrastructure

| Component | Technology | Rationale |
|---|---|---|
| **Compute** | **Google Cloud Run** | Serverless containers, scales to zero when not demoing, WebSocket support |
| **AI — Claude (Opus 4.5 + Haiku)** | **AWS Bedrock** | Managed Claude access, no self-hosting, IAM-integrated |
| **AI — Gemini 3 Flash** | **Google Vertex AI** | Native GCP integration, pairs naturally with Cloud Run deployment |
| **AI — GPT-5.2** | **OpenAI API (direct)** | Direct API — no cloud-managed wrapper needed |
| **Database** | **SQLite (demo) / PostgreSQL on RDS (prod-path)** | SQLite for zero-config demo; schema designed for easy PG/RDS migration |
| **Message Bus** | **In-memory async queue** | Simple for demo; production would use Redis Streams or SQS |
| **Container Registry** | **Google Artifact Registry** | Pairs with Cloud Run for CI/CD pipeline |
| **Secrets** | **AWS Secrets Manager** | Stores Bedrock credentials, OpenAI API key; Vertex AI uses GCP service account |

**Cloud Topology:**
```
┌─────────────────────────┐     ┌──────────────────────┐
│   Google Cloud           │     │   AWS                 │
│                         │     │                      │
│  Cloud Run (Backend)    │────▶│  Bedrock              │
│  Cloud Run (Frontend)   │     │  (Claude Opus 4.5,   │
│  Vertex AI (Gemini 3)   │     │   Claude Haiku)      │
│  Artifact Registry      │     │  Secrets Manager     │
└─────────────────────────┘     └──────────────────────┘
            │
            │ HTTPS
            ▼
    ┌──────────────┐
    │  OpenAI API   │
    │  (GPT-5.2)    │
    └──────────────┘
```

### 10.4 Project Structure

```
mundostra-demo/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── config.py                # API keys, model configs
│   ├── orchestrator/
│   │   ├── engine.py            # Core orchestration logic
│   │   └── prompts.py           # System prompts for orchestrator
│   ├── agents/
│   │   ├── base.py              # Base agent class
│   │   ├── research.py          # Gemini research agent
│   │   ├── policy.py            # Claude policy agent
│   │   └── comms.py             # OpenAI comms agent
│   ├── models/
│   │   ├── events.py            # Pydantic models for events
│   │   ├── tasks.py             # Agent task models
│   │   └── resolutions.py       # Resolution models
│   ├── mock_apis/
│   │   ├── flights.py           # Mock flight inventory
│   │   ├── calendar.py          # Mock calendar
│   │   ├── policy.py            # Mock policy engine
│   │   └── cards.py             # Mock virtual card API
│   ├── websocket/
│   │   └── trace.py             # WebSocket trace streaming
│   └── tests/
│       └── ...
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Dashboard main page
│   │   └── layout.tsx           # Root layout
│   ├── components/
│   │   ├── EventPanel.tsx       # Left panel — event details
│   │   ├── AgentStream.tsx      # Right panel — activity log
│   │   ├── JsonInspector.tsx    # Collapsible raw JSON viewer per agent step
│   │   ├── Timeline.tsx         # Resolution timeline bar
│   │   ├── CostTicker.tsx       # API cost display
│   │   ├── ConfidenceGauge.tsx  # Confidence score visual
│   │   └── TriggerButton.tsx    # "Fire demo" button
│   └── lib/
│       └── websocket.ts         # WebSocket client
├── docs/
│   ├── one-pager.md             # Written memo for Vinuta (Amazon-style)
│   └── api-reference.md         # API docs for Piyush
├── infra/
│   ├── Dockerfile.backend       # Backend container
│   ├── Dockerfile.frontend      # Frontend container
│   ├── cloudbuild.yaml          # Cloud Build CI/CD
│   └── deploy.sh                # gcloud run deploy wrapper
├── .env.example                 # Required API keys (Bedrock, Vertex AI, OpenAI)
├── Makefile                     # make demo, make test, make deploy, make reset
└── README.md
```

---

## 11. Phased Delivery Plan

This is too large to build in one shot. Each phase produces a **demoable artifact** — no phase is "just plumbing."

### Phase 1: The Orchestrator Core

**Goal:** Agents can coordinate and resolve a flight cancellation. Output is terminal/logs only — no dashboard yet.

**Deliverables:**
- FastAPI backend with event intake endpoint
- Orchestrator engine (Claude Opus 4.5 via Bedrock) — receives event, creates task plan
- Research Agent (Gemini 3 Flash via Vertex AI) — queries mock flight API, returns alternatives
- Policy Agent (Claude Haiku via Bedrock) — checks mock policy, returns compliance
- Comms Agent (GPT-5.2) — drafts Slack message text
- Mock APIs for flights, calendar, policy
- Agent trace logging (structured JSON to stdout)
- End-to-end test: trigger event → agents run → resolution produced

**Demoable at end of Phase 1:** Run from terminal, watch structured logs of agents coordinating. Proof that the multi-agent architecture works.

---

### Phase 2: The Live Dashboard

**Goal:** The visual layer that turns Phase 1 into a pitch-worthy demo.

**Deliverables:**
- Next.js dashboard with all panels from Section 7
- WebSocket connection to backend trace stream
- Real-time agent activity stream with animations
- **Collapsible JSON inspector panel** — click any agent step to see raw input/output payloads
- Resolution timeline visualization
- Cost ticker and confidence gauge
- "Trigger Demo Event" button
- Responsive layout (works on laptop screen for live demo, also on a projector/TV)
- White-labeled as **Mundostra Travel OS** (their branding, their colors)

**Demoable at end of Phase 2:** Full visual demo — click button, watch agents work, see resolution. This is the minimum viable pitch.

---

### Phase 3: Slack Integration & Polish

**Goal:** The Slack message actually arrives. The demo feels production-ready.

**Deliverables:**
- Real Slack Bot integration (Bolt SDK)
- Traveler response handling ("confirm" / "options" replies)
- Dashboard updates when traveler responds
- Virtual card mock update (authorization amount changes)
- Demo reset functionality (clean state for repeated demos)
- Error state handling (what if an agent fails? Show graceful degradation)
- Mobile-responsive dashboard refinements

**Demoable at end of Phase 3:** Full end-to-end including Slack. Traveler gets a real message, responds, and the dashboard reflects the resolution.

---

### Phase 4: The Pitch Package (Collateral)

**Goal:** Everything needed to walk into the meeting.

**Deliverables:**
- One-pager / Six-pager memo (Amazon style, for Vinuta)
- API reference doc (for Piyush — endpoints, payloads, curl examples)
- Cost analysis: "This resolution cost $0.037 in AI. A human agent costs $25+. At 500 disruptions/month, that's $12,000/month saved."
- Cloud Run deployment config (Dockerfiles + `gcloud run deploy` scripts)
- 2-minute screen recording as backup (in case live demo fails — always have a backup)
- Presentation script / talking points

**Demoable at end of Phase 4:** You're ready to pitch.

---

## 12. Success Criteria

### Technical Success

| Metric | Target |
|---|---|
| End-to-end resolution time | < 60 seconds |
| Agent parallel execution | Research + Policy run concurrently (visible on timeline) |
| API cost per resolution | < $0.10 |
| Dashboard trace latency | < 500ms from agent event to visual update |
| Zero hardcoded responses | All agent outputs are genuine LLM-generated |
| Demo reset | Clean state in < 2 seconds |

### Pitch Success

| Metric | Target |
|---|---|
| Vinuta's reaction | Asks about pricing/timeline for integration (buying signal) |
| Piyush's reaction | Asks for the repo / wants to run it himself |
| Follow-up meeting | Scheduled within 1 week |
| The "how did you build this so fast" question | They ask it — this opens the door to the sprint methodology pitch |

---

## 13. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| **API rate limits during live demo** | Medium | High — demo freezes | Pre-warm API connections; have cached fallback responses ready |
| **LLM produces unexpected output** | Medium | Medium — agent output looks weird | Structured output enforcement (JSON mode); test with 20+ runs before demo |
| **Slack delivery delay** | Low | Medium — awkward pause | Show dashboard resolution first; Slack is the "and look, it arrived" moment |
| **WiFi failure at demo location** | Low | Critical — nothing works | Cloud Run deployment means it's always live at a URL; screen recording backup as last resort |
| **Founders cancel / reschedule** | Medium | Low — no wasted work | Demo is portfolio-ready regardless; reusable for other travel-tech pitches |
| **"We can build this ourselves" objection** | High | High — they dismiss the value | Counter: "You could. But we built this in one sprint. How long would it take your team?" The speed IS the product. |
| **Confidence score too low / escalation triggered** | Low | Low — actually a feature | Show this as a positive: "The system knows its limits. It escalates to your team when uncertain." |

---

## 14. Resolved Decisions

All open questions have been answered. Documented here for the record:

| # | Question | Decision |
|---|---|---|
| 1 | Real Slack from Phase 1 or Phase 3? | **Phase 3.** Mock Slack in Phases 1-2, real integration in Phase 3. |
| 2 | Dashboard shows raw JSON alongside pretty view? | **Yes.** Collapsible JSON inspector panel per agent step. Added to dashboard spec and Phase 2 deliverables. |
| 3 | Multiple scenarios or just flight cancellation? | **One scenario (flight cancellation).** Verbally mention others run on the same framework. |
| 4 | Cloud deployment or local-only? | **Cloud Run (GCP).** Always-live URL for remote demos. Local dev via Docker as well. |
| 5 | Include Price Truth Auditor as second scenario? | **No.** Mention verbally as "Sprint 2" deliverable. |
| 6 | Model versions? | **Claude Opus 4.5** (orchestrator, via AWS Bedrock), **Gemini 3 Flash** (research, via Vertex AI), **Claude Haiku latest** (policy, via AWS Bedrock), **GPT-5.2** (comms, OpenAI direct). |
| 7 | White-label or our brand? | **White-label as Mundostra.** Dashboard branded as Mundostra Travel OS. |
| 8 | Voice agent for card pre-check? | **Deferred to Phase 5.** Focus on the core self-healing support agent first. |

---

## 15. Phase Summary

| Phase | What It Delivers | Key Tech |
|---|---|---|
| **Phase 1** | Multi-agent orchestration working in terminal | FastAPI + Bedrock + Vertex AI + OpenAI |
| **Phase 2** | Live dashboard with real-time agent visualization + JSON inspector | Next.js + WebSocket + Framer Motion |
| **Phase 3** | Real Slack integration, traveler responses, full loop | Slack Bolt SDK, demo reset, error handling |
| **Phase 4** | Pitch collateral (memo, API docs, cost analysis, screen recording) | Documentation + Cloud Run deploy |
| **Phase 5** *(future)* | Voice agent for card pre-checks, Price Truth Auditor | Vapi/Bland AI, browser extension |

---

*This is a living document. Updated 2026-02-11 with all decisions resolved.*

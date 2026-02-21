// TypeScript interfaces mirroring backend Pydantic models

export type EventType =
  | 'flight_cancelled'
  | 'flight_delayed'
  | 'card_declined'
  | 'hotel_overbooked';

export type PolicyTier = 'standard' | 'manager' | 'executive';

export type ResolutionStatus = 'proposed' | 'confirmed' | 'rejected' | 'escalated';

export type AgentName = 'orchestrator' | 'research' | 'policy' | 'comms';

export type TaskStatus = 'pending' | 'running' | 'complete' | 'failed';

export type TraceStatus = 'thinking' | 'working' | 'complete' | 'error' | 'escalation';

export interface FlightDetails {
  number: string;
  origin: string;
  destination: string;
  scheduled_departure: string;
  status: string;
  reason: string | null;
  original_price: number;
}

export interface TravelerProfile {
  id: string;
  name: string;
  email: string;
  role: string;
  policy_tier: PolicyTier;
  messaging_id: string;
  timezone: string;
  calendar_integration: boolean;
  preferences: Record<string, unknown>;
}

export interface TravelEvent {
  id: string;
  event_type: EventType;
  timestamp: string;
  booking_ref: string;
  flight: FlightDetails | null;
  traveler: TravelerProfile;
  metadata: Record<string, unknown>;
}

export interface FlightAlternative {
  flight: string;
  departure: string;
  arrival: string;
  price: number;
  calendar_conflict: boolean;
  conflict_details: string | null;
  price_vs_original: string;
  seat_available: boolean;
  source: string;
}

export interface ResearchResult {
  alternatives: FlightAlternative[];
  recommendation: string;
  search_metadata: Record<string, unknown>;
}

export interface PolicyEvaluation {
  flight: string;
  price: number;
  budget_status: string;
  approval_required: boolean;
  policy_notes: string;
  compliant: boolean;
}

export interface PolicyResult {
  policy_evaluation: PolicyEvaluation[];
  auto_approve_eligible: boolean;
  escalation_required: boolean;
  policy_version: string;
}

export interface CommsResult {
  channel: string;
  text: string;
  tone_score: string;
  urgency_flag: string;
  email_sent?: boolean;
}

export interface Resolution {
  id: string;
  event_id: string;
  status: ResolutionStatus;
  chosen_option: FlightAlternative | null;
  confidence_score: number;
  policy_compliant: boolean;
  total_cost_usd: number;
  total_time_seconds: number;
  agents_involved: string[];
  research_result: ResearchResult | null;
  policy_result: PolicyResult | null;
  comms_result: CommsResult | null;
  ticket_pdf_url?: string | null;
  created_at: string;
}

export interface AgentTraceEntry {
  timestamp: string;
  event_id: string;
  agent: AgentName;
  model: string;
  status: TraceStatus;
  message: string;
  tokens_used: number;
  cost_usd: number;
  data: Record<string, unknown> | null;
}

export interface TraceResponse {
  event_id: string;
  trace_count: number;
  trace: AgentTraceEntry[];
}

export type TravelerResponseType = 'confirm' | 'options' | 'reject';

export interface TravelerResponsePayload {
  event_id: string;
  response_type: TravelerResponseType;
}

export interface ResetResponse {
  status: string;
}

export interface HealthResponse {
  status: string;
}

// Chat types
export interface ChatApiResponse {
  session_id: string;
  intent: string;
  acknowledgment: string;
  event_id?: string;
  status?: string;
  resolution?: Resolution;
}

export interface ChatStatusApiResponse {
  status: 'processing' | 'complete' | 'error';
  event_id: string;
  resolution?: Resolution;
}

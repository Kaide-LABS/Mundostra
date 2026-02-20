import type {
  TravelEvent,
  Resolution,
  TraceResponse,
  TravelerResponseType,
  ResetResponse,
  HealthResponse,
  ChatApiResponse,
  ChatStatusApiResponse,
} from '@/types';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  });
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<HealthResponse>('/health'),

  triggerEvent: (event: TravelEvent) =>
    request<Resolution>('/api/events', {
      method: 'POST',
      body: JSON.stringify(event),
    }),

  getResolution: (eventId: string) => request<Resolution>(`/api/events/${eventId}`),

  getTrace: (eventId: string) => request<TraceResponse>(`/api/events/${eventId}/trace`),

  respondToEvent: (eventId: string, responseType: TravelerResponseType) =>
    request<Resolution>(`/api/events/${eventId}/respond`, {
      method: 'POST',
      body: JSON.stringify({ event_id: eventId, response_type: responseType }),
    }),

  resetDemo: () =>
    request<ResetResponse>('/api/reset', {
      method: 'POST',
    }),

  sendChatMessage: (message: string, sessionId?: string) =>
    request<ChatApiResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    }),

  getChatStatus: (eventId: string) =>
    request<ChatStatusApiResponse>(`/api/chat/status/${eventId}`),
};

'use client';

import {
  createContext,
  useContext,
  useReducer,
  useRef,
  useCallback,
  type ReactNode,
} from 'react';
import type { Resolution } from '@/types';
import { api } from '@/lib/api';

// ── Types ──────────────────────────────────────────────

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  resolution?: Resolution;
  showOptions?: boolean;
  imagePreview?: string;
  ticketPdfUrl?: string;
}

export interface ChatState {
  messages: ChatMessage[];
  sessionId: string;
  activeEventId: string | null;
  isProcessing: boolean;
  showChips: boolean;
  ticketPdfUrl: string | null;
}

const initialState: ChatState = {
  messages: [
    {
      id: 'welcome',
      role: 'assistant',
      content:
        "Hello! I'm your Mundostra travel assistant. I can help you when flights get cancelled or delayed. Tell me what happened, or snap a photo of your boarding pass to get started.",
      timestamp: new Date(),
    },
  ],
  sessionId: crypto.randomUUID(),
  activeEventId: null,
  isProcessing: false,
  showChips: true,
  ticketPdfUrl: null,
};

// ── Actions ────────────────────────────────────────────

type Action =
  | { type: 'ADD_USER_MESSAGE'; content: string; imagePreview?: string }
  | { type: 'ADD_ASSISTANT_MESSAGE'; content: string; resolution?: Resolution; showOptions?: boolean; ticketPdfUrl?: string }
  | { type: 'SET_PROCESSING'; processing: boolean }
  | { type: 'SET_EVENT_ID'; eventId: string }
  | { type: 'HIDE_CHIPS' }
  | { type: 'RESET' };

function reducer(state: ChatState, action: Action): ChatState {
  switch (action.type) {
    case 'ADD_USER_MESSAGE':
      return {
        ...state,
        messages: [
          ...state.messages,
          {
            id: crypto.randomUUID(),
            role: 'user',
            content: action.content,
            timestamp: new Date(),
            imagePreview: action.imagePreview,
          },
        ],
        showChips: false,
      };
    case 'ADD_ASSISTANT_MESSAGE':
      return {
        ...state,
        messages: [
          ...state.messages,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: action.content,
            timestamp: new Date(),
            resolution: action.resolution,
            showOptions: action.showOptions,
            ticketPdfUrl: action.ticketPdfUrl,
          },
        ],
        ticketPdfUrl: action.ticketPdfUrl ?? state.ticketPdfUrl,
      };
    case 'SET_PROCESSING':
      return { ...state, isProcessing: action.processing };
    case 'SET_EVENT_ID':
      return { ...state, activeEventId: action.eventId };
    case 'HIDE_CHIPS':
      return { ...state, showChips: false };
    case 'RESET':
      return { ...initialState, sessionId: crypto.randomUUID(), ticketPdfUrl: null };
    default:
      return state;
  }
}

// ── Context ────────────────────────────────────────────

interface ChatContextValue {
  state: ChatState;
  sendMessage: (content: string) => Promise<void>;
  sendImage: (imageBase64: string) => Promise<void>;
  reset: () => void;
}

const ChatContext = createContext<ChatContextValue | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const pollForResolution = useCallback(
    (eventId: string) => {
      dispatch({ type: 'SET_PROCESSING', processing: true });
      dispatch({
        type: 'ADD_ASSISTANT_MESSAGE',
        content: 'Working on it — searching for alternative flights, checking your calendar, and reviewing travel policy...',
      });

      pollingRef.current = setInterval(async () => {
        try {
          const status = await api.getChatStatus(eventId);
          if (status.status === 'complete' && status.resolution) {
            if (pollingRef.current) clearInterval(pollingRef.current);
            dispatch({ type: 'SET_PROCESSING', processing: false });

            const r = status.resolution;
            const chosen = r.chosen_option;
            if (chosen) {
              const dep = new Date(chosen.departure).toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
              });
              dispatch({
                type: 'ADD_ASSISTANT_MESSAGE',
                content: `Great news! I found you a new flight: **${chosen.flight}** departing at **${dep}** for **$${chosen.price}**. No calendar conflicts detected and it's within your travel policy. Shall I book this one?`,
                resolution: r,
                showOptions: true,
              });
            } else {
              dispatch({
                type: 'ADD_ASSISTANT_MESSAGE',
                content: "I've looked into alternatives but couldn't find a strong match. Let me connect you with a human agent who can help further.",
              });
            }
          } else if (status.status === 'error') {
            if (pollingRef.current) clearInterval(pollingRef.current);
            dispatch({ type: 'SET_PROCESSING', processing: false });
            dispatch({
              type: 'ADD_ASSISTANT_MESSAGE',
              content: 'Sorry, something went wrong while processing your request. Please try again.',
            });
          }
        } catch {
          // Network error — keep polling
        }
      }, 2000);
    },
    [],
  );

  const sendMessage = useCallback(
    async (content: string) => {
      dispatch({ type: 'ADD_USER_MESSAGE', content });
      dispatch({ type: 'SET_PROCESSING', processing: true });

      try {
        const response = await api.sendChatMessage(content, state.sessionId);

        if (response.status === 'gathering') {
          // Gathering mode: show the question, stay idle (no polling)
          dispatch({ type: 'SET_PROCESSING', processing: false });
          dispatch({
            type: 'ADD_ASSISTANT_MESSAGE',
            content: response.acknowledgment,
          });
        } else if (response.intent === 'flight_disruption' && response.event_id) {
          dispatch({ type: 'SET_EVENT_ID', eventId: response.event_id });
          dispatch({ type: 'ADD_ASSISTANT_MESSAGE', content: response.acknowledgment });
          pollForResolution(response.event_id);
        } else if (response.status === 'processing' && response.event_id) {
          // Gathering complete → orchestration triggered
          dispatch({ type: 'SET_EVENT_ID', eventId: response.event_id });
          dispatch({ type: 'ADD_ASSISTANT_MESSAGE', content: response.acknowledgment });
          pollForResolution(response.event_id);
        } else if (
          (response.intent === 'confirm' || response.intent === 'options' || response.intent === 'reject') &&
          response.resolution
        ) {
          dispatch({ type: 'SET_PROCESSING', processing: false });

          if (response.intent === 'confirm') {
            const pdfUrl = response.resolution?.ticket_pdf_url;
            dispatch({
              type: 'ADD_ASSISTANT_MESSAGE',
              content: "Confirmed! Your new flight has been booked and a virtual card has been authorized. You'll receive a confirmation email shortly.",
              resolution: response.resolution,
              ticketPdfUrl: pdfUrl ?? undefined,
            });
          } else if (response.intent === 'options') {
            const alts = response.resolution.research_result?.alternatives ?? [];
            let msg = `Here are all ${alts.length} available alternatives:\n\n`;
            alts.forEach((a, i) => {
              const dep = new Date(a.departure).toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
              });
              const conflict = a.calendar_conflict ? ' (calendar conflict)' : '';
              msg += `${i + 1}. **${a.flight}** — ${dep}, $${a.price}${conflict}\n`;
            });
            msg += '\nWould you like to book any of these, or should I connect you with an agent?';
            dispatch({
              type: 'ADD_ASSISTANT_MESSAGE',
              content: msg,
              resolution: response.resolution,
            });
          } else {
            dispatch({
              type: 'ADD_ASSISTANT_MESSAGE',
              content: "I understand. I'm escalating this to a human agent who will reach out to you shortly.",
            });
          }
        } else {
          dispatch({ type: 'SET_PROCESSING', processing: false });
          dispatch({
            type: 'ADD_ASSISTANT_MESSAGE',
            content: response.acknowledgment,
          });
        }
      } catch {
        dispatch({ type: 'SET_PROCESSING', processing: false });
        dispatch({
          type: 'ADD_ASSISTANT_MESSAGE',
          content: 'Sorry, I had trouble connecting to the server. Please try again.',
        });
      }
    },
    [state.sessionId, pollForResolution],
  );

  const sendImage = useCallback(
    async (imageBase64: string) => {
      dispatch({ type: 'ADD_USER_MESSAGE', content: 'Uploaded boarding pass photo', imagePreview: imageBase64 });
      dispatch({ type: 'SET_PROCESSING', processing: true });
      dispatch({ type: 'ADD_ASSISTANT_MESSAGE', content: 'Scanning your boarding pass...' });

      try {
        const response = await api.sendChatMessage('', state.sessionId, imageBase64);

        if (response.status === 'gathering') {
          dispatch({ type: 'SET_PROCESSING', processing: false });
          dispatch({ type: 'ADD_ASSISTANT_MESSAGE', content: response.acknowledgment });
        } else if (response.status === 'processing' && response.event_id) {
          dispatch({ type: 'SET_EVENT_ID', eventId: response.event_id });
          dispatch({ type: 'ADD_ASSISTANT_MESSAGE', content: response.acknowledgment });
          pollForResolution(response.event_id);
        } else {
          dispatch({ type: 'SET_PROCESSING', processing: false });
          dispatch({ type: 'ADD_ASSISTANT_MESSAGE', content: response.acknowledgment });
        }
      } catch {
        dispatch({ type: 'SET_PROCESSING', processing: false });
        dispatch({
          type: 'ADD_ASSISTANT_MESSAGE',
          content: 'Sorry, I had trouble processing that image. Please try again or type your flight details.',
        });
      }
    },
    [state.sessionId, pollForResolution],
  );

  const reset = useCallback(() => {
    if (pollingRef.current) clearInterval(pollingRef.current);
    api.resetDemo().catch(() => {});
    dispatch({ type: 'RESET' });
  }, []);

  return (
    <ChatContext.Provider value={{ state, sendMessage, sendImage, reset }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChat(): ChatContextValue {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChat must be used within ChatProvider');
  return ctx;
}

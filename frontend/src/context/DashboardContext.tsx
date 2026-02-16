'use client';

import {
  createContext,
  useContext,
  useReducer,
  useEffect,
  useRef,
  useCallback,
  type ReactNode,
} from 'react';
import type { TravelEvent, Resolution, AgentTraceEntry, TravelerResponseType } from '@/types';
import { DEMO_EVENT } from '@/types';
import { api } from '@/lib/api';
import { createWsClient, type WsStatus, type WsClient } from '@/lib/websocket';

// ── State ──────────────────────────────────────────────

export interface DashboardState {
  wsStatus: WsStatus;
  currentEvent: TravelEvent | null;
  traceEntries: AgentTraceEntry[];
  resolution: Resolution | null;
  isRunning: boolean;
  isResetting: boolean;
  isResponding: boolean;
  selectedTraceIndex: number | null;
}

const initialState: DashboardState = {
  wsStatus: 'closed',
  currentEvent: null,
  traceEntries: [],
  resolution: null,
  isRunning: false,
  isResetting: false,
  isResponding: false,
  selectedTraceIndex: null,
};

// ── Actions ────────────────────────────────────────────

type Action =
  | { type: 'WS_STATUS'; status: WsStatus }
  | { type: 'START_RUN'; event: TravelEvent }
  | { type: 'TRACE_ENTRY'; entry: AgentTraceEntry }
  | { type: 'RESOLUTION'; resolution: Resolution }
  | { type: 'RESOLUTION_UPDATE'; resolution: Resolution }
  | { type: 'RUN_ERROR' }
  | { type: 'SELECT_TRACE'; index: number | null }
  | { type: 'RESET_START' }
  | { type: 'RESET' }
  | { type: 'RESPOND_START' }
  | { type: 'RESPOND_END' };

function reducer(state: DashboardState, action: Action): DashboardState {
  switch (action.type) {
    case 'WS_STATUS':
      return { ...state, wsStatus: action.status };
    case 'START_RUN':
      return {
        ...state,
        currentEvent: action.event,
        traceEntries: [],
        resolution: null,
        isRunning: true,
        selectedTraceIndex: null,
      };
    case 'TRACE_ENTRY':
      return {
        ...state,
        traceEntries: [...state.traceEntries, action.entry],
      };
    case 'RESOLUTION':
      return { ...state, resolution: action.resolution, isRunning: false };
    case 'RESOLUTION_UPDATE':
      return { ...state, resolution: action.resolution, isResponding: false };
    case 'RUN_ERROR':
      return { ...state, isRunning: false };
    case 'SELECT_TRACE':
      return {
        ...state,
        selectedTraceIndex: state.selectedTraceIndex === action.index ? null : action.index,
      };
    case 'RESET_START':
      return { ...state, isResetting: true };
    case 'RESET':
      return { ...initialState, wsStatus: state.wsStatus };
    case 'RESPOND_START':
      return { ...state, isResponding: true };
    case 'RESPOND_END':
      return { ...state, isResponding: false };
    default:
      return state;
  }
}

// ── Context ────────────────────────────────────────────

interface DashboardContextValue {
  state: DashboardState;
  dispatch: React.Dispatch<Action>;
  triggerDemo: () => Promise<void>;
  reset: () => Promise<void>;
  respondToEvent: (responseType: TravelerResponseType) => Promise<void>;
}

const DashboardContext = createContext<DashboardContextValue | null>(null);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  const wsRef = useRef<WsClient | null>(null);

  useEffect(() => {
    const client = createWsClient(
      (entry) => dispatch({ type: 'TRACE_ENTRY', entry }),
      (status) => dispatch({ type: 'WS_STATUS', status }),
    );
    wsRef.current = client;
    client.connect();
    return () => client.disconnect();
  }, []);

  const triggerDemo = useCallback(async () => {
    const event: TravelEvent = {
      ...DEMO_EVENT,
      id: crypto.randomUUID(),
      timestamp: new Date().toISOString(),
    };
    dispatch({ type: 'START_RUN', event });

    try {
      const resolution = await api.triggerEvent(event);
      dispatch({ type: 'RESOLUTION', resolution });
    } catch {
      dispatch({ type: 'RUN_ERROR' });
    }
  }, []);

  const reset = useCallback(async () => {
    dispatch({ type: 'RESET_START' });
    try {
      await api.resetDemo();
    } catch {
      // Reset frontend state even if backend call fails
    }
    dispatch({ type: 'RESET' });
  }, []);

  const respondToEvent = useCallback(
    async (responseType: TravelerResponseType) => {
      if (!state.currentEvent) return;
      dispatch({ type: 'RESPOND_START' });
      try {
        const updated = await api.respondToEvent(state.currentEvent.id, responseType);
        dispatch({ type: 'RESOLUTION_UPDATE', resolution: updated });
      } catch {
        dispatch({ type: 'RESPOND_END' });
      }
    },
    [state.currentEvent],
  );

  return (
    <DashboardContext.Provider value={{ state, dispatch, triggerDemo, reset, respondToEvent }}>
      {children}
    </DashboardContext.Provider>
  );
}

export function useDashboard(): DashboardContextValue {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error('useDashboard must be used within DashboardProvider');
  return ctx;
}

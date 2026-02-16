import type { AgentTraceEntry } from '@/types';

export type WsStatus = 'connecting' | 'open' | 'closed' | 'error';

export interface WsClient {
  connect: () => void;
  disconnect: () => void;
  getStatus: () => WsStatus;
}

const WS_URL = process.env.NEXT_PUBLIC_WS_URL ?? 'ws://localhost:8000/ws/trace';
const RECONNECT_DELAY = 2000;
const PING_INTERVAL = 25000;

export function createWsClient(
  onMessage: (entry: AgentTraceEntry) => void,
  onStatusChange: (status: WsStatus) => void,
): WsClient {
  let ws: WebSocket | null = null;
  let pingTimer: ReturnType<typeof setInterval> | null = null;
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  let status: WsStatus = 'closed';
  let intentionalClose = false;

  function setStatus(s: WsStatus) {
    status = s;
    onStatusChange(s);
  }

  function clearTimers() {
    if (pingTimer) {
      clearInterval(pingTimer);
      pingTimer = null;
    }
    if (reconnectTimer) {
      clearTimeout(reconnectTimer);
      reconnectTimer = null;
    }
  }

  function connect() {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      return;
    }

    intentionalClose = false;
    setStatus('connecting');

    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setStatus('open');
      pingTimer = setInterval(() => {
        if (ws?.readyState === WebSocket.OPEN) {
          ws.send('ping');
        }
      }, PING_INTERVAL);
    };

    ws.onmessage = (event) => {
      if (event.data === 'pong') return;
      try {
        const entry = JSON.parse(event.data) as AgentTraceEntry;
        onMessage(entry);
      } catch {
        // ignore non-JSON messages
      }
    };

    ws.onclose = () => {
      clearTimers();
      setStatus('closed');
      if (!intentionalClose) {
        reconnectTimer = setTimeout(connect, RECONNECT_DELAY);
      }
    };

    ws.onerror = () => {
      setStatus('error');
    };
  }

  function disconnect() {
    intentionalClose = true;
    clearTimers();
    if (ws) {
      ws.close();
      ws = null;
    }
    setStatus('closed');
  }

  return {
    connect,
    disconnect,
    getStatus: () => status,
  };
}

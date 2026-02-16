'use client';

import { useDashboard } from '@/context/DashboardContext';

const WS_COLORS = {
  open: 'bg-green-500',
  connecting: 'bg-amber-500 animate-pulse',
  closed: 'bg-gray-500',
  error: 'bg-red-500',
};

export function ControlBar() {
  const { state, triggerDemo, reset } = useDashboard();

  return (
    <div className="flex items-center justify-between rounded-xl border border-white/5 bg-bg-surface px-4 py-3">
      <div className="flex flex-col gap-2 sm:flex-row sm:gap-3">
        <button
          onClick={triggerDemo}
          disabled={state.isRunning}
          className="min-h-[44px] rounded-lg bg-violet-600 px-5 py-2 text-sm font-semibold text-white transition-colors hover:bg-violet-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {state.isRunning ? (
            <span className="flex items-center gap-2">
              <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              Processing...
            </span>
          ) : (
            'Trigger Demo Event'
          )}
        </button>

        <button
          onClick={reset}
          disabled={state.isRunning || state.isResetting}
          className="min-h-[44px] rounded-lg border border-white/10 px-5 py-2 text-sm font-medium text-gray-300 transition-colors hover:bg-bg-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          {state.isResetting ? (
            <span className="flex items-center gap-2">
              <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/30 border-t-white" />
              Resetting...
            </span>
          ) : (
            'Reset'
          )}
        </button>
      </div>

      <div className="flex items-center gap-2 text-xs text-gray-400">
        <span>WebSocket</span>
        <span className={`h-2.5 w-2.5 rounded-full ${WS_COLORS[state.wsStatus]}`} />
        <span className="capitalize">{state.wsStatus}</span>
      </div>
    </div>
  );
}

'use client';

import { useEffect, useRef } from 'react';
import { useDashboard } from '@/context/DashboardContext';
import { AgentStreamEntry } from '@/components/AgentStreamEntry';

export function AgentStream() {
  const { state, dispatch } = useDashboard();
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [state.traceEntries.length]);

  return (
    <div className="flex h-full flex-col">
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-400">
        Agent Activity Stream
      </h2>

      <div className="agent-stream flex-1 space-y-0.5 overflow-y-auto rounded-xl border border-white/5 bg-bg-surface p-2">
        {state.traceEntries.length === 0 ? (
          <div className="flex h-full items-center justify-center">
            <p className="text-sm text-gray-600">Waiting for agent activity...</p>
          </div>
        ) : (
          state.traceEntries.map((entry, i) => (
            <AgentStreamEntry
              key={`${entry.timestamp}-${i}`}
              entry={entry}
              index={i}
              isExpanded={state.selectedTraceIndex === i}
              onToggle={() => dispatch({ type: 'SELECT_TRACE', index: i })}
            />
          ))
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}

'use client';

import type { TraceStatus } from '@/types';

const STATUS_CONFIG: Record<TraceStatus, { label: string; bg: string; text: string }> = {
  thinking: { label: 'Thinking', bg: 'bg-violet-500/20', text: 'text-violet-400' },
  working: { label: 'Working', bg: 'bg-cyan-500/20', text: 'text-cyan-400' },
  complete: { label: 'Complete', bg: 'bg-green-500/20', text: 'text-green-400' },
  error: { label: 'Error', bg: 'bg-red-500/20', text: 'text-red-400' },
  escalation: { label: 'Escalation', bg: 'bg-amber-500/20', text: 'text-amber-400' },
};

export function StatusBadge({ status }: { status: TraceStatus }) {
  const cfg = STATUS_CONFIG[status];
  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${cfg.bg} ${cfg.text}`}
    >
      {status === 'thinking' || status === 'working' ? (
        <span className="mr-1.5 h-1.5 w-1.5 animate-pulse rounded-full bg-current" />
      ) : null}
      {cfg.label}
    </span>
  );
}

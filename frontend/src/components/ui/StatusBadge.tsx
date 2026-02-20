'use client';

import type { TraceStatus } from '@/types';

const STATUS_CONFIG: Record<TraceStatus, { label: string; bg: string; text: string }> = {
  thinking: { label: 'Thinking', bg: 'bg-violet-100', text: 'text-violet-700' },
  working: { label: 'Working', bg: 'bg-cyan-100', text: 'text-cyan-700' },
  complete: { label: 'Complete', bg: 'bg-green-100', text: 'text-green-700' },
  error: { label: 'Error', bg: 'bg-red-100', text: 'text-red-700' },
  escalation: { label: 'Escalation', bg: 'bg-amber-100', text: 'text-amber-700' },
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

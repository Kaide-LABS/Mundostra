'use client';

import { motion } from 'framer-motion';
import type { AgentTraceEntry } from '@/types';
import { AgentIcon, agentLabel } from '@/components/ui/AgentIcon';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { JsonInspector } from '@/components/JsonInspector';

interface Props {
  entry: AgentTraceEntry;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}

export function AgentStreamEntry({ entry, index, isExpanded, onToggle }: Props) {
  const time = new Date(entry.timestamp).toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  const isError = entry.status === 'error';
  const errorData = isError && entry.data?.error ? String(entry.data.error) : null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, delay: index * 0.03 }}
      className="group"
    >
      <button
        onClick={onToggle}
        className={`flex min-h-[44px] w-full items-start gap-3 rounded-lg px-3 py-2.5 text-left transition-colors hover:bg-bg-hover ${
          isError ? 'border-l-2 border-red-500 bg-red-500/5' : ''
        }`}
      >
        <AgentIcon agent={entry.agent} size="sm" />

        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-gray-300">{agentLabel(entry.agent)}</span>
            <StatusBadge status={entry.status} />
            <span className="ml-auto hidden font-mono text-[10px] text-gray-600 sm:inline">
              {time}
            </span>
          </div>
          <p className={`mt-0.5 text-sm ${isError ? 'font-medium text-red-400' : 'text-gray-400'}`}>
            {entry.message}
          </p>
          {errorData && (
            <pre className="mt-1 overflow-x-auto rounded bg-red-500/10 p-1.5 font-mono text-[11px] text-red-300">
              {errorData}
            </pre>
          )}
          {(entry.tokens_used > 0 || entry.cost_usd > 0) && (
            <div className="mt-1 flex gap-3 text-[10px] text-gray-600">
              {entry.model && <span>{entry.model.split('/').pop()}</span>}
              {entry.tokens_used > 0 && <span>{entry.tokens_used} tok</span>}
              {entry.cost_usd > 0 && <span>${entry.cost_usd.toFixed(4)}</span>}
            </div>
          )}
        </div>
      </button>

      {isExpanded && entry.data && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="ml-12 mb-2 overflow-hidden rounded-lg border border-white/5 bg-[#0d1117] p-3"
        >
          <JsonInspector data={entry.data} />
        </motion.div>
      )}
    </motion.div>
  );
}

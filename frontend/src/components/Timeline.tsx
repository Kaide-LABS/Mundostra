'use client';

import { useDashboard } from '@/context/DashboardContext';
import { buildTimeline } from '@/context/selectors';
import { agentLabel } from '@/components/ui/AgentIcon';
import type { AgentName } from '@/types';

const AGENT_COLORS: Record<AgentName, string> = {
  orchestrator: '#8b5cf6',
  research: '#06b6d4',
  policy: '#f59e0b',
  comms: '#22c55e',
};

const BAR_HEIGHT = 24;
const ROW_GAP = 8;
const LABEL_WIDTH = 100;
const PADDING = 16;

export function Timeline() {
  const { state } = useDashboard();
  const spans = buildTimeline(state.traceEntries);

  if (spans.length === 0) {
    return (
      <div className="flex h-24 items-center justify-center rounded-xl border border-gray-200 bg-white shadow-sm text-sm text-gray-400">
        Timeline will appear during agent execution
      </div>
    );
  }

  const maxEnd = Math.max(...spans.map((s) => s.end), 1);
  const svgHeight = spans.length * (BAR_HEIGHT + ROW_GAP) + PADDING;
  const barAreaWidth = 600;

  return (
    <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm p-3">
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-wider text-gray-500">
        Parallel Execution Timeline
      </h2>
      <svg
        width="100%"
        height={svgHeight}
        viewBox={`0 0 ${LABEL_WIDTH + barAreaWidth + PADDING} ${svgHeight}`}
        className="w-full"
      >
        {spans.map((span, i) => {
          const y = i * (BAR_HEIGHT + ROW_GAP) + PADDING / 2;
          const x = LABEL_WIDTH + (span.start / maxEnd) * barAreaWidth;
          const width = Math.max(((span.end - span.start) / maxEnd) * barAreaWidth, 4);

          return (
            <g key={span.agent}>
              <text
                x={LABEL_WIDTH - 8}
                y={y + BAR_HEIGHT / 2}
                textAnchor="end"
                dominantBaseline="central"
                className="fill-gray-500 text-xs"
                fontSize={11}
              >
                {agentLabel(span.agent)}
              </text>
              <rect
                x={x}
                y={y}
                width={width}
                height={BAR_HEIGHT}
                rx={4}
                fill={AGENT_COLORS[span.agent]}
                opacity={0.8}
              >
                <animate attributeName="width" from="0" to={width} dur="0.6s" fill="freeze" />
              </rect>
              <text
                x={x + width + 6}
                y={y + BAR_HEIGHT / 2}
                dominantBaseline="central"
                className="fill-gray-400"
                fontSize={10}
              >
                {span.end - span.start > 0
                  ? `${((span.end - span.start) / 1000).toFixed(1)}s`
                  : '<1s'}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}

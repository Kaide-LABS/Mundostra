'use client';

import { useDashboard } from '@/context/DashboardContext';
import { modelUsage } from '@/context/selectors';
import { Card } from '@/components/ui/Card';

export function ModelUsage() {
  const { state } = useDashboard();
  const models = modelUsage(state.traceEntries);

  return (
    <Card className="flex flex-col">
      <span className="text-xs font-semibold uppercase tracking-wider text-gray-400">
        Model Usage
      </span>

      {models.length === 0 ? (
        <p className="mt-2 text-sm text-gray-600">No model calls yet</p>
      ) : (
        <div className="mt-2 space-y-2">
          {models.map((m) => (
            <div key={m.model} className="rounded-lg bg-bg-hover/50 px-3 py-2">
              <div className="font-mono text-xs text-gray-300">{m.model.split('/').pop()}</div>
              <div className="mt-1 flex gap-4 text-[10px] text-gray-500">
                <span>{m.calls} calls</span>
                <span>{m.tokens.toLocaleString()} tok</span>
                <span>${m.cost.toFixed(4)}</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {state.resolution && (
        <div className="mt-auto pt-3 text-xs text-gray-500">
          Total time: {state.resolution.total_time_seconds.toFixed(1)}s
        </div>
      )}
    </Card>
  );
}

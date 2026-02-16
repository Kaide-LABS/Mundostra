import type { AgentTraceEntry, AgentName } from '@/types';

export function totalCost(entries: AgentTraceEntry[]): number {
  return entries.reduce((sum, e) => sum + e.cost_usd, 0);
}

export function totalTokens(entries: AgentTraceEntry[]): number {
  return entries.reduce((sum, e) => sum + e.tokens_used, 0);
}

export interface AgentTimelineSpan {
  agent: AgentName;
  start: number;
  end: number;
}

export function buildTimeline(entries: AgentTraceEntry[]): AgentTimelineSpan[] {
  if (entries.length === 0) return [];

  const globalStart = new Date(entries[0].timestamp).getTime();
  const byAgent = new Map<AgentName, { start: number; end: number }>();

  for (const e of entries) {
    const t = new Date(e.timestamp).getTime() - globalStart;
    const existing = byAgent.get(e.agent);
    if (!existing) {
      byAgent.set(e.agent, { start: t, end: t });
    } else {
      existing.end = t;
    }
  }

  return Array.from(byAgent.entries()).map(([agent, span]) => ({
    agent,
    ...span,
  }));
}

export interface ModelUsageSummary {
  model: string;
  calls: number;
  tokens: number;
  cost: number;
}

export function modelUsage(entries: AgentTraceEntry[]): ModelUsageSummary[] {
  const map = new Map<string, ModelUsageSummary>();
  for (const e of entries) {
    if (!e.model) continue;
    const existing = map.get(e.model);
    if (!existing) {
      map.set(e.model, { model: e.model, calls: 1, tokens: e.tokens_used, cost: e.cost_usd });
    } else {
      existing.calls++;
      existing.tokens += e.tokens_used;
      existing.cost += e.cost_usd;
    }
  }
  return Array.from(map.values());
}

export function groupByAgent(entries: AgentTraceEntry[]): Map<AgentName, AgentTraceEntry[]> {
  const map = new Map<AgentName, AgentTraceEntry[]>();
  for (const e of entries) {
    const arr = map.get(e.agent) ?? [];
    arr.push(e);
    map.set(e.agent, arr);
  }
  return map;
}

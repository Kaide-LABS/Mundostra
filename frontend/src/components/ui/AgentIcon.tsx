'use client';

import type { AgentName } from '@/types';

const AGENT_CONFIG: Record<AgentName, { letter: string; color: string }> = {
  orchestrator: { letter: 'O', color: 'bg-agent-orchestrator' },
  research: { letter: 'R', color: 'bg-agent-research' },
  policy: { letter: 'P', color: 'bg-agent-policy' },
  comms: { letter: 'C', color: 'bg-agent-comms' },
};

export function AgentIcon({ agent, size = 'md' }: { agent: AgentName; size?: 'sm' | 'md' }) {
  const cfg = AGENT_CONFIG[agent];
  const sizeClass = size === 'sm' ? 'h-6 w-6 text-xs' : 'h-8 w-8 text-sm';
  return (
    <div
      className={`${cfg.color} ${sizeClass} flex shrink-0 items-center justify-center rounded-full font-bold text-white`}
    >
      {cfg.letter}
    </div>
  );
}

export function agentLabel(agent: AgentName): string {
  return agent.charAt(0).toUpperCase() + agent.slice(1);
}

'use client';

import Image from 'next/image';
import { DashboardProvider } from '@/context/DashboardContext';
import { EventPanel } from '@/components/EventPanel';
import { AgentStream } from '@/components/AgentStream';
import { Timeline } from '@/components/Timeline';
import { CostTicker } from '@/components/CostTicker';
import { ConfidenceGauge } from '@/components/ConfidenceGauge';
import { ModelUsage } from '@/components/ModelUsage';
import { ControlBar } from '@/components/ControlBar';

function Dashboard() {
  return (
    <div className="flex min-h-screen flex-col gap-3 overflow-x-hidden p-2 sm:p-4">
      {/* Header */}
      <header className="flex items-center justify-between rounded-xl border border-gray-200 bg-white shadow-sm px-3 py-2 sm:px-5 sm:py-3">
        <div className="flex items-center gap-3">
          <Image
            src="/logo.png"
            alt="Mundostra"
            width={32}
            height={32}
            className="rounded-lg"
          />
          <div>
            <h1 className="text-sm font-bold tracking-wide text-gray-900">MUNDOSTRA TRAVEL OS</h1>
            <p className="text-[10px] uppercase tracking-widest text-gray-400">
              Agent Command Center
            </p>
          </div>
        </div>
        <span className="font-mono text-[10px] text-gray-400">v0.1.0</span>
      </header>

      {/* Main Grid: EventPanel + AgentStream */}
      <div className="grid min-h-0 flex-1 gap-3 lg:grid-cols-[380px_1fr]">
        <div className="min-h-[300px] lg:min-h-0">
          <EventPanel />
        </div>
        <div className="min-h-[400px] lg:min-h-0">
          <AgentStream />
        </div>
      </div>

      {/* Timeline */}
      <Timeline />

      {/* Metrics Row */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <CostTicker />
        <ConfidenceGauge />
        <ModelUsage />
      </div>

      {/* Control Bar */}
      <ControlBar />
    </div>
  );
}

export default function Home() {
  return (
    <DashboardProvider>
      <Dashboard />
    </DashboardProvider>
  );
}

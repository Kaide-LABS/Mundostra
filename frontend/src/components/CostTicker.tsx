'use client';

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { useDashboard } from '@/context/DashboardContext';
import { totalCost, totalTokens } from '@/context/selectors';
import { Card } from '@/components/ui/Card';

export function CostTicker() {
  const { state } = useDashboard();
  const target = totalCost(state.traceEntries);
  const tokens = totalTokens(state.traceEntries);
  const [displayed, setDisplayed] = useState(0);

  useEffect(() => {
    if (target === 0) {
      setDisplayed(0);
      return;
    }
    const start = displayed;
    const diff = target - start;
    const steps = 20;
    let step = 0;

    const timer = setInterval(() => {
      step++;
      setDisplayed(start + (diff * step) / steps);
      if (step >= steps) clearInterval(timer);
    }, 30);

    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [target]);

  return (
    <Card className="flex flex-col items-center justify-center text-center">
      <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
        Total Cost
      </span>
      <motion.span
        className="mt-1 font-mono text-2xl font-bold text-green-600"
        key={target}
        initial={{ scale: 1.1 }}
        animate={{ scale: 1 }}
      >
        ${displayed.toFixed(4)}
      </motion.span>
      <span className="mt-1 text-xs text-gray-500">{tokens.toLocaleString()} tokens</span>
    </Card>
  );
}

'use client';

import { motion } from 'framer-motion';
import { useDashboard } from '@/context/DashboardContext';
import { Card } from '@/components/ui/Card';

export function ConfidenceGauge() {
  const { state } = useDashboard();
  const score = state.resolution?.confidence_score ?? 0;

  const radius = 60;
  const stroke = 8;
  const cx = 80;
  const cy = 70;
  const startAngle = Math.PI;
  const endAngle = 0;
  const totalArc = startAngle - endAngle;

  const arcPath = (fraction: number) => {
    const angle = startAngle - totalArc * fraction;
    const x = cx + radius * Math.cos(angle);
    const y = cy - radius * Math.sin(angle);
    const startX = cx + radius * Math.cos(startAngle);
    const startY = cy - radius * Math.sin(startAngle);
    const largeArc = fraction > 0.5 ? 1 : 0;
    return `M ${startX} ${startY} A ${radius} ${radius} 0 ${largeArc} 1 ${x} ${y}`;
  };

  const scoreColor = score >= 0.8 ? '#22c55e' : score >= 0.5 ? '#f59e0b' : '#ef4444';

  return (
    <Card className="flex flex-col items-center justify-center text-center">
      <span className="text-xs font-semibold uppercase tracking-wider text-gray-500">
        Confidence
      </span>
      <svg width={160} height={90} className="mt-1">
        {/* Background arc */}
        <path
          d={arcPath(1)}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        {/* Score arc */}
        {score > 0 && (
          <motion.path
            d={arcPath(score)}
            fill="none"
            stroke={scoreColor}
            strokeWidth={stroke}
            strokeLinecap="round"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
          />
        )}
        <text
          x={cx}
          y={cy - 5}
          textAnchor="middle"
          dominantBaseline="central"
          className="font-mono text-xl font-bold"
          fill={score > 0 ? scoreColor : '#6b7280'}
        >
          {score > 0 ? (score * 100).toFixed(0) + '%' : '--'}
        </text>
        <text x={20} y={cy + 12} className="text-[9px]" fill="#9ca3af">
          0
        </text>
        <text x={140} y={cy + 12} textAnchor="end" className="text-[9px]" fill="#9ca3af">
          100
        </text>
      </svg>
    </Card>
  );
}

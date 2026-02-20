'use client';

import { motion } from 'framer-motion';
import type { Resolution } from '@/types';

interface Props {
  resolution: Resolution;
  onConfirm: () => void;
  onOptions: () => void;
}

export function ResolutionCard({ resolution, onConfirm, onOptions }: Props) {
  const chosen = resolution.chosen_option;
  if (!chosen) return null;

  const dep = new Date(chosen.departure).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });
  const arr = new Date(chosen.arrival).toLocaleTimeString('en-US', {
    hour: 'numeric',
    minute: '2-digit',
  });

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="mx-4 rounded-xl border border-purple-200 bg-gradient-to-br from-purple-50 to-white p-4 shadow-sm"
    >
      <div className="flex items-center gap-2 mb-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-full bg-purple-100">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="rgb(147 51 234)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z" />
          </svg>
        </div>
        <div>
          <p className="text-sm font-semibold text-gray-900">{chosen.flight}</p>
          <p className="text-xs text-gray-500">{chosen.source}</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-3 text-center">
        <div>
          <p className="text-xs text-gray-400 uppercase">Departs</p>
          <p className="text-sm font-medium text-gray-800">{dep}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase">Arrives</p>
          <p className="text-sm font-medium text-gray-800">{arr}</p>
        </div>
        <div>
          <p className="text-xs text-gray-400 uppercase">Price</p>
          <p className="text-sm font-medium text-gray-800">${chosen.price}</p>
        </div>
      </div>

      <div className="flex items-center gap-2 mb-3 text-xs">
        {!chosen.calendar_conflict && (
          <span className="rounded-full bg-green-100 px-2 py-0.5 text-green-700">No conflicts</span>
        )}
        {resolution.policy_compliant && (
          <span className="rounded-full bg-blue-100 px-2 py-0.5 text-blue-700">Policy OK</span>
        )}
        <span className="rounded-full bg-purple-100 px-2 py-0.5 text-purple-700">
          {(resolution.confidence_score * 100).toFixed(0)}% confidence
        </span>
      </div>

      <div className="flex gap-2">
        <button
          onClick={onConfirm}
          className="flex-1 rounded-lg bg-purple-600 py-2 text-sm font-medium text-white transition-colors hover:bg-purple-700"
        >
          Confirm Booking
        </button>
        <button
          onClick={onOptions}
          className="flex-1 rounded-lg border border-gray-300 bg-white py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50"
        >
          See Options
        </button>
      </div>
    </motion.div>
  );
}

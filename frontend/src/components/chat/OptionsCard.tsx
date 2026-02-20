'use client';

import { motion } from 'framer-motion';
import type { FlightAlternative } from '@/types';

interface Props {
  alternatives: FlightAlternative[];
}

export function OptionsCard({ alternatives }: Props) {
  if (!alternatives.length) return null;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="mx-4 rounded-xl border border-gray-200 bg-white p-3 shadow-sm space-y-2"
    >
      <p className="text-xs font-medium text-gray-500 uppercase tracking-wide">Available Flights</p>
      {alternatives.map((alt, i) => {
        const dep = new Date(alt.departure).toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
        });
        return (
          <div
            key={alt.flight}
            className={`flex items-center justify-between rounded-lg p-2.5 text-sm ${
              alt.calendar_conflict
                ? 'bg-red-50 border border-red-100'
                : i === 0
                  ? 'bg-purple-50 border border-purple-100'
                  : 'bg-gray-50 border border-gray-100'
            }`}
          >
            <div>
              <span className="font-medium text-gray-900">{alt.flight}</span>
              <span className="ml-2 text-gray-500">{dep}</span>
            </div>
            <div className="flex items-center gap-2">
              {alt.calendar_conflict && (
                <span className="text-xs text-red-600">Conflict</span>
              )}
              <span className="font-medium text-gray-800">${alt.price}</span>
            </div>
          </div>
        );
      })}
    </motion.div>
  );
}

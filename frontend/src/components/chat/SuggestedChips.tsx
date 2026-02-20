'use client';

import { motion } from 'framer-motion';

const SUGGESTIONS = [
  'My flight UA 2381 got cancelled',
  'My flight from SFO to JFK is delayed',
  'I need to rebook a cancelled flight',
];

interface Props {
  onSelect: (message: string) => void;
}

export function SuggestedChips({ onSelect }: Props) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.3 }}
      className="flex flex-wrap gap-2 px-4"
    >
      <p className="w-full text-xs text-gray-400 mb-1">Try one of these:</p>
      {SUGGESTIONS.map((s) => (
        <button
          key={s}
          onClick={() => onSelect(s)}
          className="rounded-full border border-purple-200 bg-purple-50 px-3 py-1.5 text-xs font-medium text-purple-700 transition-colors hover:bg-purple-100 hover:border-purple-300"
        >
          {s}
        </button>
      ))}
    </motion.div>
  );
}

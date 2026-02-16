import type { Config } from 'tailwindcss';

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          DEFAULT: '#0a0e1a',
          surface: '#111827',
          hover: '#1f2937',
        },
        agent: {
          orchestrator: '#8b5cf6',
          research: '#06b6d4',
          policy: '#f59e0b',
          comms: '#22c55e',
        },
        accent: {
          violet: '#8b5cf6',
          cyan: '#06b6d4',
          amber: '#f59e0b',
          green: '#22c55e',
          red: '#ef4444',
        },
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-jetbrains)', 'monospace'],
      },
    },
  },
  plugins: [],
};
export default config;

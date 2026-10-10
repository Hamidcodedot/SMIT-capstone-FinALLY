import type { Config } from 'tailwindcss';

const config: Config = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        base: {
          bg: '#080a0f',
          surface: '#0d111a',
          panel: '#111622',
          card: '#151b2a',
          hover: '#1b2234',
          border: '#1f273b',
          borderSubtle: '#181e2d',
        },
        accent: {
          brand: '#10b981',
          emerald: '#10b981',
          cyan: '#06b6d4',
          indigo: '#6366f1',
          amber: '#f59e0b',
          rose: '#f43f5e',
          yellow: '#f59e0b',
          blue: '#06b6d4',
          purple: '#8b5cf6',
        },
        up: '#10b981',
        down: '#f43f5e',
      },
      fontFamily: {
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'Consolas', 'monospace'],
        sans: ['system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
      keyframes: {
        'flash-up': {
          '0%': { backgroundColor: 'rgba(16, 185, 129, 0.40)' },
          '100%': { backgroundColor: 'transparent' },
        },
        'flash-down': {
          '0%': { backgroundColor: 'rgba(244, 63, 94, 0.40)' },
          '100%': { backgroundColor: 'transparent' },
        },
        'pulse-subtle': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.4' },
        },
      },
      animation: {
        'flash-up': 'flash-up 600ms ease-out',
        'flash-down': 'flash-down 600ms ease-out',
        'pulse-subtle': 'pulse-subtle 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      },
    },
  },
  plugins: [],
};

export default config;

'use client';

import { useState } from 'react';
import { TICKER_UNIVERSE } from '@/lib/types';
import type { TradeSide } from '@/lib/types';

interface TradeBarProps {
  selectedTicker: string | null;
  onTrade: (ticker: string, quantity: number, side: TradeSide) => Promise<void> | void;
  errorMessage: string | null;
}

const PRESET_QUANTITIES = ['1', '5', '10', '25'];

export default function TradeBar({ selectedTicker, onTrade, errorMessage }: TradeBarProps) {
  const [ticker, setTicker] = useState(selectedTicker ?? TICKER_UNIVERSE[0]);
  const [quantity, setQuantity] = useState('1');
  const [submitting, setSubmitting] = useState(false);

  const activeTicker = selectedTicker ?? ticker;

  const submit = async (side: TradeSide) => {
    const qty = Number(quantity);
    if (!Number.isFinite(qty) || qty <= 0) return;
    setSubmitting(true);
    try {
      await onTrade(activeTicker, qty, side);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <section className="rounded-lg border border-base-border bg-base-panel/90 p-3.5 shadow-sm">
      <div className="mb-2.5 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <svg className="h-3.5 w-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="2" y="3" width="20" height="14" rx="2" />
            <line x1="8" y1="21" x2="16" y2="21" />
            <line x1="12" y1="17" x2="12" y2="21" />
          </svg>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300">Trade Deck</h2>
        </div>
        <span className="font-mono text-[11px] font-bold text-emerald-400">
          {activeTicker}
        </span>
      </div>

      {/* Preset Qty Pills */}
      <div className="mb-2.5 flex items-center gap-1.5 text-[11px]">
        <span className="text-slate-500">Quick:</span>
        {PRESET_QUANTITIES.map((q) => (
          <button
            key={q}
            type="button"
            onClick={() => setQuantity(q)}
            className={`rounded border px-2 py-0.5 font-mono text-[10px] transition ${
              quantity === q
                ? 'border-emerald-500/50 bg-emerald-950/50 text-emerald-300'
                : 'border-base-border bg-base-card text-slate-400 hover:border-slate-600 hover:text-slate-200'
            }`}
          >
            {q}
          </button>
        ))}
      </div>

      {/* Inputs and Execution Deck */}
      <div className="flex flex-wrap items-center gap-2">
        <select
          value={activeTicker}
          onChange={(e) => setTicker(e.target.value)}
          disabled={!!selectedTicker}
          className="rounded border border-base-border bg-base-card px-2.5 py-1.5 text-xs font-mono font-medium text-slate-200 outline-none transition focus:border-emerald-500/50 disabled:opacity-70"
        >
          {TICKER_UNIVERSE.map((t) => (
            <option key={t} value={t}>
              {t}
            </option>
          ))}
        </select>

        <input
          type="number"
          min="1"
          step="any"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          className="w-20 rounded border border-base-border bg-base-card px-2.5 py-1.5 text-xs font-mono text-slate-200 outline-none transition focus:border-emerald-500/50"
          placeholder="Qty"
        />

        <div className="flex flex-1 items-center gap-1.5 sm:flex-initial">
          <button
            type="button"
            disabled={submitting}
            onClick={() => submit('buy')}
            className="flex-1 rounded bg-emerald-600 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-white shadow-sm transition hover:bg-emerald-500 active:scale-[0.98] disabled:opacity-50 sm:flex-initial"
          >
            Buy
          </button>

          <button
            type="button"
            disabled={submitting}
            onClick={() => submit('sell')}
            className="flex-1 rounded bg-rose-600 px-4 py-1.5 text-xs font-bold uppercase tracking-wider text-white shadow-sm transition hover:bg-rose-500 active:scale-[0.98] disabled:opacity-50 sm:flex-initial"
          >
            Sell
          </button>
        </div>
      </div>

      {errorMessage && (
        <div className="mt-2.5 flex items-center gap-1.5 rounded border border-rose-900/60 bg-rose-950/40 px-2.5 py-1.5 text-xs text-rose-300">
          <svg className="h-3.5 w-3.5 flex-shrink-0 text-rose-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
          <span>{errorMessage}</span>
        </div>
      )}
    </section>
  );
}

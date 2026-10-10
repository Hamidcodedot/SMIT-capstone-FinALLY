'use client';

import { useState } from 'react';
import Sparkline from './Sparkline';
import PriceFlash from './PriceFlash';
import type { PricePoint, PriceTick } from '@/lib/types';
import { TICKER_UNIVERSE } from '@/lib/types';

interface WatchlistPanelProps {
  tickers: string[];
  prices: Record<string, PriceTick>;
  history: Record<string, PricePoint[]>;
  selectedTicker: string | null;
  onSelect: (ticker: string) => void;
  onAdd: (ticker: string) => void;
  onRemove: (ticker: string) => void;
}

export default function WatchlistPanel({
  tickers,
  prices,
  history,
  selectedTicker,
  onSelect,
  onAdd,
  onRemove,
}: WatchlistPanelProps) {
  const [pendingAdd, setPendingAdd] = useState('');
  const addable = TICKER_UNIVERSE.filter((t) => !tickers.includes(t));

  return (
    <section className="flex h-full flex-col rounded-lg border border-base-border bg-base-panel/90 shadow-sm">
      {/* Header Deck */}
      <div className="flex items-center justify-between border-b border-base-border px-3.5 py-2.5">
        <div className="flex items-center gap-2">
          <svg className="h-3.5 w-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="8" y1="6" x2="21" y2="6" />
            <line x1="8" y1="12" x2="21" y2="12" />
            <line x1="8" y1="18" x2="21" y2="18" />
            <line x1="3" y1="6" x2="3.01" y2="6" />
            <line x1="3" y1="12" x2="3.01" y2="12" />
            <line x1="3" y1="18" x2="3.01" y2="18" />
          </svg>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300">Watchlist</h2>
          <span className="rounded bg-base-card px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
            {tickers.length}
          </span>
        </div>

        {addable.length > 0 && (
          <div className="flex items-center gap-1.5">
            <select
              value={pendingAdd}
              onChange={(e) => setPendingAdd(e.target.value)}
              className="rounded border border-base-border bg-base-card px-2 py-0.5 text-xs font-mono text-slate-200 outline-none transition focus:border-emerald-500/50"
            >
              <option value="">+ Ticker</option>
              {addable.map((t) => (
                <option key={t} value={t}>
                  {t}
                </option>
              ))}
            </select>
            <button
              type="button"
              disabled={!pendingAdd}
              onClick={() => {
                if (!pendingAdd) return;
                onAdd(pendingAdd);
                setPendingAdd('');
              }}
              className="rounded bg-emerald-600 px-2.5 py-0.5 text-xs font-medium text-white transition hover:bg-emerald-500 disabled:opacity-40"
            >
              Add
            </button>
          </div>
        )}
      </div>

      {/* Tickers Table */}
      <div className="flex-1 overflow-y-auto">
        <table className="w-full text-xs">
          <thead className="sticky top-0 z-10 border-b border-base-border/70 bg-base-panel/95 text-[11px] uppercase tracking-wider text-slate-500 backdrop-blur-sm">
            <tr>
              <th className="px-3 py-2 text-left font-medium">Symbol</th>
              <th className="px-2 py-2 text-right font-medium">Price</th>
              <th className="px-2 py-2 text-right font-medium">Change</th>
              <th className="px-2 py-2 text-right font-medium">Trend</th>
              <th className="w-7 py-2" />
            </tr>
          </thead>
          <tbody className="divide-y divide-base-border/40">
            {tickers.map((ticker) => {
              const tick = prices[ticker];
              const pts = history[ticker] ?? [];
              const isSelected = ticker === selectedTicker;
              const isUp = tick && tick.change_percent > 0;
              const isDown = tick && tick.change_percent < 0;

              return (
                <tr
                  key={ticker}
                  onClick={() => onSelect(ticker)}
                  className={`group cursor-pointer transition-colors ${
                    isSelected
                      ? 'border-l-2 border-l-emerald-400 bg-emerald-500/[0.08]'
                      : 'border-l-2 border-l-transparent hover:bg-slate-800/40'
                  }`}
                >
                  <td className="px-3 py-2">
                    <span className="font-mono font-bold tracking-tight text-slate-100 group-hover:text-emerald-400">
                      {ticker}
                    </span>
                  </td>
                  <td className="px-2 py-2 text-right font-mono text-slate-200">
                    {tick ? (
                      <PriceFlash direction={tick.direction} flashKey={tick.timestamp}>
                        ${tick.price.toFixed(2)}
                      </PriceFlash>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>
                  <td className="px-2 py-2 text-right font-mono">
                    {tick ? (
                      <span
                        className={`inline-flex items-center gap-0.5 rounded px-1.5 py-0.5 text-[11px] font-medium ${
                          isUp
                            ? 'bg-emerald-950/60 text-emerald-400'
                            : isDown
                              ? 'bg-rose-950/60 text-rose-400'
                              : 'text-slate-400'
                        }`}
                      >
                        {isUp && (
                          <svg className="h-2.5 w-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                            <polyline points="18 15 12 9 6 15" />
                          </svg>
                        )}
                        {isDown && (
                          <svg className="h-2.5 w-2.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                            <polyline points="6 9 12 15 18 9" />
                          </svg>
                        )}
                        {`${tick.change_percent >= 0 ? '+' : ''}${tick.change_percent.toFixed(2)}%`}
                      </span>
                    ) : (
                      <span className="text-slate-600">—</span>
                    )}
                  </td>
                  <td className="px-2 py-2 text-right">
                    <Sparkline points={pts} />
                  </td>
                  <td className="px-1 py-2 text-right">
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRemove(ticker);
                      }}
                      className="rounded p-1 text-slate-500 opacity-60 transition hover:bg-rose-500/10 hover:text-rose-400 group-hover:opacity-100"
                      aria-label={`Remove ${ticker} from watchlist`}
                    >
                      <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                        <line x1="18" y1="6" x2="6" y2="18" />
                        <line x1="6" y1="6" x2="18" y2="18" />
                      </svg>
                    </button>
                  </td>
                </tr>
              );
            })}
            {tickers.length === 0 && (
              <tr>
                <td colSpan={5} className="px-3 py-8 text-center text-slate-500">
                  Watchlist is empty
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

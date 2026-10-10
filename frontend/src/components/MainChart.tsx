'use client';

import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import PriceFlash from './PriceFlash';
import type { PricePoint, PriceTick } from '@/lib/types';

interface MainChartProps {
  ticker: string | null;
  points: PricePoint[];
  tick: PriceTick | undefined;
}

export default function MainChart({ ticker, points, tick }: MainChartProps) {
  const data = points.map((p) => ({
    time: new Date(p.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
    price: p.price,
  }));

  const isUp = tick ? tick.direction !== 'down' : true;
  const strokeColor = isUp ? '#10b981' : '#f43f5e';
  const prices = points.map((p) => p.price);
  const sessionHigh = prices.length > 0 ? Math.max(...prices).toFixed(2) : null;
  const sessionLow = prices.length > 0 ? Math.min(...prices).toFixed(2) : null;

  return (
    <section className="flex h-full flex-col rounded-lg border border-base-border bg-base-panel/90 p-3.5 shadow-sm">
      {/* Chart Header Bar */}
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2 border-b border-base-border/50 pb-2.5">
        <div className="flex items-center gap-2.5">
          <div className="flex items-center gap-2">
            <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse" />
            <h2 className="font-mono text-lg font-bold tracking-tight text-white">
              {ticker ?? 'Select a ticker'}
            </h2>
          </div>
          <span className="rounded bg-base-card px-2 py-0.5 text-[10px] font-mono uppercase tracking-wider text-slate-400">
            GBM STREAM
          </span>
        </div>

        {tick && (
          <div className="flex items-center gap-3 font-mono">
            {sessionHigh && sessionLow && (
              <div className="hidden gap-2 text-[11px] text-slate-400 md:flex">
                <span>H: <span className="text-slate-200">${sessionHigh}</span></span>
                <span>L: <span className="text-slate-200">${sessionLow}</span></span>
              </div>
            )}
            <div className="flex items-baseline gap-2">
              <PriceFlash direction={tick.direction} flashKey={tick.timestamp} className="text-xl font-bold text-white">
                ${tick.price.toFixed(2)}
              </PriceFlash>
              <span
                className={`rounded px-1.5 py-0.5 text-xs font-semibold ${
                  tick.change_percent >= 0
                    ? 'bg-emerald-950/60 text-emerald-400'
                    : 'bg-rose-950/60 text-rose-400'
                }`}
              >
                {tick.change_percent >= 0 ? '+' : ''}
                {tick.change_percent.toFixed(2)}%
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Interactive Chart Canvas */}
      <div className="min-h-0 flex-1">
        {data.length > 1 ? (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 6, right: 10, bottom: 0, left: 0 }}>
              <defs>
                <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={strokeColor} stopOpacity={0.30} />
                  <stop offset="95%" stopColor={strokeColor} stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1c2333" vertical={false} />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#64748b' }} minTickGap={45} axisLine={{ stroke: '#1c2333' }} />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fontSize: 10, fill: '#64748b' }}
                width={56}
                axisLine={{ stroke: '#1c2333' }}
                tickFormatter={(v: number) => `$${v.toFixed(2)}`}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0d111a',
                  borderColor: '#1f273b',
                  borderRadius: '6px',
                  boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
                  fontSize: '11px',
                  fontFamily: 'ui-monospace, monospace',
                }}
                labelStyle={{ color: '#94a3b8' }}
                itemStyle={{ color: '#f1f5f9' }}
                formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
              />
              <Area
                type="monotone"
                dataKey="price"
                stroke={strokeColor}
                fill="url(#chartFill)"
                strokeWidth={2}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-2 text-sm text-slate-500">
            <svg className="h-8 w-8 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <line x1="18" y1="20" x2="18" y2="10" />
              <line x1="12" y1="20" x2="12" y2="4" />
              <line x1="6" y1="20" x2="6" y2="14" />
            </svg>
            <span>{ticker ? 'Awaiting streaming ticks…' : 'Select a symbol from the watchlist to render analytics'}</span>
          </div>
        )}
      </div>
    </section>
  );
}

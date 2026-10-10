'use client';

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { PortfolioSnapshot } from '@/lib/types';

interface PnLChartProps {
  snapshots: PortfolioSnapshot[];
}

export default function PnLChart({ snapshots }: PnLChartProps) {
  const data = snapshots.map((s) => ({
    time: new Date(s.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    value: s.total_value,
  }));

  return (
    <section className="flex h-full flex-col rounded-lg border border-base-border bg-base-panel/90 p-3 shadow-sm">
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <svg className="h-3.5 w-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
            <polyline points="17 6 23 6 23 12" />
          </svg>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300">Portfolio Value</h2>
        </div>
        <span className="text-[10px] font-mono text-slate-500">30S SNAPSHOTS</span>
      </div>

      <div className="min-h-0 flex-1">
        {data.length > 1 ? (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 6, right: 10, bottom: 0, left: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1c2333" vertical={false} />
              <XAxis dataKey="time" tick={{ fontSize: 10, fill: '#64748b' }} minTickGap={40} axisLine={{ stroke: '#1c2333' }} />
              <YAxis
                domain={['auto', 'auto']}
                tick={{ fontSize: 10, fill: '#64748b' }}
                width={56}
                axisLine={{ stroke: '#1c2333' }}
                tickFormatter={(v: number) => `$${v.toFixed(0)}`}
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
                itemStyle={{ color: '#06b6d4' }}
                formatter={(val: number) => [`$${val.toFixed(2)}`, 'Valuation']}
              />
              <Line
                type="monotone"
                dataKey="value"
                stroke="#06b6d4"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full items-center justify-center text-xs text-slate-500">
            Awaiting valuation history snapshots…
          </div>
        )}
      </div>
    </section>
  );
}

import type { Position } from '@/lib/types';

function formatUsd(value: number): string {
  return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

export default function PositionsTable({ positions }: { positions: Position[] }) {
  return (
    <section className="flex h-full flex-col rounded-lg border border-base-border bg-base-panel/90 shadow-sm">
      <div className="flex items-center justify-between border-b border-base-border px-3.5 py-2.5">
        <div className="flex items-center gap-1.5">
          <svg className="h-3.5 w-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="2" y="7" width="20" height="14" rx="2" ry="2" />
            <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16" />
          </svg>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300">Positions</h2>
          <span className="rounded bg-base-card px-1.5 py-0.5 text-[10px] font-mono text-slate-400">
            {positions.length} ACTIVE
          </span>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <table className="w-full text-xs">
          <thead className="sticky top-0 z-10 border-b border-base-border/70 bg-base-panel/95 text-[11px] uppercase tracking-wider text-slate-500 backdrop-blur-sm">
            <tr>
              <th className="px-3 py-2 text-left font-medium">Symbol</th>
              <th className="px-2 py-2 text-right font-medium">Qty</th>
              <th className="px-2 py-2 text-right font-medium">Avg Cost</th>
              <th className="px-2 py-2 text-right font-medium">Price</th>
              <th className="px-2 py-2 text-right font-medium">P&amp;L</th>
              <th className="px-3 py-2 text-right font-medium">%</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-base-border/40">
            {positions.map((p) => {
              const isProfit = p.unrealized_pnl >= 0;
              return (
                <tr key={p.ticker} className="transition-colors hover:bg-slate-800/40">
                  <td className="px-3 py-2 font-mono font-bold text-slate-100">{p.ticker}</td>
                  <td className="px-2 py-2 text-right font-mono text-slate-300">{p.quantity}</td>
                  <td className="px-2 py-2 text-right font-mono text-slate-400">{formatUsd(p.avg_cost)}</td>
                  <td className="px-2 py-2 text-right font-mono font-medium text-slate-200">{formatUsd(p.current_price)}</td>
                  <td className={`px-2 py-2 text-right font-mono font-medium ${isProfit ? 'text-up' : 'text-down'}`}>
                    {isProfit ? '+' : ''}
                    {formatUsd(p.unrealized_pnl)}
                  </td>
                  <td className="px-3 py-2 text-right font-mono">
                    <span
                      className={`inline-block rounded px-1.5 py-0.5 text-[10px] font-semibold ${
                        isProfit ? 'bg-emerald-950/60 text-emerald-400' : 'bg-rose-950/60 text-rose-400'
                      }`}
                    >
                      {isProfit ? '+' : ''}
                      {p.pnl_percent.toFixed(2)}%
                    </span>
                  </td>
                </tr>
              );
            })}
            {positions.length === 0 && (
              <tr>
                <td colSpan={6} className="px-3 py-8 text-center text-slate-500">
                  No open positions
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}

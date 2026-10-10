import ConnectionStatus from './ConnectionStatus';
import type { ConnectionState } from '@/lib/types';

function formatUsd(value: number): string {
  return value.toLocaleString('en-US', { style: 'currency', currency: 'USD' });
}

interface HeaderProps {
  totalValue: number;
  cashBalance: number;
  connectionState: ConnectionState;
}

export default function Header({ totalValue, cashBalance, connectionState }: HeaderProps) {
  const buyingPowerPct = totalValue > 0 ? ((cashBalance / totalValue) * 100).toFixed(0) : '100';
  const totalReturn = totalValue - 10000;
  const returnPct = ((totalReturn / 10000) * 100).toFixed(2);

  return (
    <header className="flex flex-wrap items-center justify-between border-b border-base-border bg-base-surface/80 px-4 py-2.5 backdrop-blur-md sm:px-6">
      {/* Brand & Terminal Meta */}
      <div className="flex items-center gap-3">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-emerald-500/30 bg-emerald-950/40 text-emerald-400 shadow-sm">
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="22 7 13.5 15.5 8.5 10.5 2 17" />
            <polyline points="16 7 22 7 22 13" />
          </svg>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-base font-bold tracking-tight text-white sm:text-lg">FinAlly</span>
          <span className="hidden rounded border border-base-border bg-base-card px-1.5 py-0.5 text-[10px] font-mono uppercase tracking-wider text-emerald-400 sm:inline-block">
            QUANT TERMINAL
          </span>
        </div>
      </div>

      {/* Real-time KPI Metric Deck */}
      <div className="flex items-center gap-4 sm:gap-7">
        {/* Portfolio Value */}
        <div className="rounded-md border border-base-border/50 bg-base-card/60 px-3 py-1 text-right">
          <div className="flex items-center justify-end gap-1.5 text-[10px] uppercase tracking-wider text-slate-400">
            <span>PORTFOLIO VALUE</span>
            <span className={`font-mono text-[9px] font-semibold ${totalReturn >= 0 ? 'text-up' : 'text-down'}`}>
              {totalReturn >= 0 ? '+' : ''}{returnPct}%
            </span>
          </div>
          <div className="font-mono text-sm font-bold tracking-tight text-slate-100 sm:text-base">
            {formatUsd(totalValue)}
          </div>
        </div>

        {/* Cash Balance */}
        <div className="rounded-md border border-base-border/50 bg-base-card/60 px-3 py-1 text-right">
          <div className="flex items-center justify-end gap-1.5 text-[10px] uppercase tracking-wider text-slate-400">
            <span>AVAILABLE CASH</span>
            <span className="font-mono text-[9px] text-cyan-400">({buyingPowerPct}% LIQUID)</span>
          </div>
          <div className="font-mono text-sm font-semibold tracking-tight text-cyan-300 sm:text-base">
            {formatUsd(cashBalance)}
          </div>
        </div>

        {/* Real-Time SSE Stream Heartbeat */}
        <ConnectionStatus state={connectionState} />
      </div>
    </header>
  );
}

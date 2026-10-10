'use client';

import { ResponsiveContainer, Treemap } from 'recharts';
import type { Position } from '@/lib/types';

interface PortfolioHeatmapProps {
  positions: Position[];
}

function colorForPnlPercent(pct: number): string {
  const clamped = Math.max(-10, Math.min(10, pct));
  const intensity = Math.abs(clamped) / 10;
  if (pct >= 0) {
    const g = Math.round(110 + intensity * 90);
    return `rgb(10, ${g}, 80)`;
  }
  const r = Math.round(140 + intensity * 90);
  return `rgb(${r}, 35, 60)`;
}

interface HeatmapNode {
  name: string;
  size: number;
  pnlPercent: number;
}

function CellContent(props: { x?: number; y?: number; width?: number; height?: number; payload?: HeatmapNode }) {
  const { x = 0, y = 0, width = 0, height = 0, payload } = props;
  if (!payload || width < 2 || height < 2) return null;
  const showLabel = width > 45 && height > 28;
  return (
    <g>
      <rect
        x={x}
        y={y}
        width={width}
        height={height}
        rx={4}
        fill={colorForPnlPercent(payload.pnlPercent)}
        stroke="#080a0f"
        strokeWidth={2}
      />
      {showLabel && (
        <text x={x + 8} y={y + 16} fill="#f8fafc" fontSize={11} fontWeight={700} fontFamily="ui-monospace, monospace">
          {payload.name}
        </text>
      )}
      {showLabel && (
        <text x={x + 8} y={y + 30} fill="#e2e8f0" fontSize={10} fontFamily="ui-monospace, monospace">
          {payload.pnlPercent >= 0 ? '+' : ''}
          {payload.pnlPercent.toFixed(1)}%
        </text>
      )}
    </g>
  );
}

export default function PortfolioHeatmap({ positions }: PortfolioHeatmapProps) {
  const data: HeatmapNode[] = positions.map((p) => ({
    name: p.ticker,
    size: Math.max(p.quantity * p.current_price, 0.01),
    pnlPercent: p.pnl_percent,
  }));

  return (
    <section className="flex h-full flex-col rounded-lg border border-base-border bg-base-panel/90 p-3 shadow-sm">
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-1.5">
          <svg className="h-3.5 w-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <rect x="3" y="3" width="7" height="7" />
            <rect x="14" y="3" width="7" height="7" />
            <rect x="14" y="14" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" />
          </svg>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300">Portfolio Heatmap</h2>
        </div>
        <span className="text-[10px] font-mono text-slate-500">BY WEIGHT</span>
      </div>

      <div className="min-h-0 flex-1">
        {data.length > 0 ? (
          <ResponsiveContainer width="100%" height="100%">
            <Treemap data={data} dataKey="size" stroke="#080a0f" content={<CellContent />} isAnimationActive={false} />
          </ResponsiveContainer>
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-1 text-xs text-slate-500">
            <svg className="h-6 w-6 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21.21 15.89A10 10 0 1 1 8 2.83" />
              <path d="M22 12A10 10 0 0 0 12 2v10z" />
            </svg>
            <span>No open positions</span>
          </div>
        )}
      </div>
    </section>
  );
}

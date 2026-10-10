import type { ConnectionState } from '@/lib/types';

const CONFIG: Record<ConnectionState, { dotColor: string; pingColor: string; label: string; badgeBg: string }> = {
  connected: {
    dotColor: 'bg-emerald-400',
    pingColor: 'bg-emerald-500',
    label: 'SSE ACTIVE',
    badgeBg: 'bg-emerald-950/40 border-emerald-800/40 text-emerald-400',
  },
  reconnecting: {
    dotColor: 'bg-amber-400',
    pingColor: 'bg-amber-500',
    label: 'SYNCING…',
    badgeBg: 'bg-amber-950/40 border-amber-800/40 text-amber-400',
  },
  disconnected: {
    dotColor: 'bg-rose-400',
    pingColor: 'bg-rose-500',
    label: 'OFFLINE',
    badgeBg: 'bg-rose-950/40 border-rose-800/40 text-rose-400',
  },
};

export default function ConnectionStatus({ state }: { state: ConnectionState }) {
  const { dotColor, pingColor, label, badgeBg } = CONFIG[state];
  return (
    <div className={`flex items-center gap-2 rounded-full border px-2.5 py-1 text-[11px] font-mono tracking-wider ${badgeBg}`}>
      <span className="relative flex h-2 w-2">
        {state === 'connected' && (
          <span className={`absolute inline-flex h-full w-full animate-ping rounded-full opacity-75 ${pingColor}`} />
        )}
        <span className={`relative inline-flex h-2 w-2 rounded-full ${dotColor}`} />
      </span>
      <span className="font-medium">{label}</span>
    </div>
  );
}

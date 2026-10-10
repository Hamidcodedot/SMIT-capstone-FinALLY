'use client';

import { useEffect, useRef, useState } from 'react';
import type { ChatMessage } from '@/lib/types';

interface ChatPanelProps {
  messages: ChatMessage[];
  onSend: (content: string) => Promise<void> | void;
  isLoading: boolean;
}

const PROMPT_SUGGESTIONS = [
  'Analyze portfolio risk exposure',
  'Buy 5 shares of AAPL',
  'What is my total return?',
];

export default function ChatPanel({ messages, onSend, isLoading }: ChatPanelProps) {
  const [draft, setDraft] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight });
  }, [messages, isLoading]);

  const submit = async () => {
    const content = draft.trim();
    if (!content) return;
    setDraft('');
    await onSend(content);
  };

  const selectSuggestion = (text: string) => {
    setDraft(text);
  };

  return (
    <section className="flex h-full flex-col rounded-lg border border-base-border bg-base-panel/90 shadow-sm">
      {/* Header Deck */}
      <div className="flex items-center justify-between border-b border-base-border px-3.5 py-2.5">
        <div className="flex items-center gap-2">
          <div className="flex h-5 w-5 items-center justify-center rounded bg-emerald-950/60 text-emerald-400 border border-emerald-800/40">
            <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <path d="M12 2a2 2 0 0 1 2 2v2a2 2 0 0 1-2 2 2 2 0 0 1-2-2V4a2 2 0 0 1 2-2z" />
              <rect x="4" y="8" width="16" height="12" rx="2" />
              <line x1="8" y1="13" x2="8.01" y2="13" strokeWidth="3" />
              <line x1="16" y1="13" x2="16.01" y2="13" strokeWidth="3" />
            </svg>
          </div>
          <h2 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
            FinAlly Assistant
          </h2>
        </div>
        <span className="flex items-center gap-1.5 rounded-full border border-emerald-900/40 bg-emerald-950/40 px-2 py-0.5 text-[10px] font-mono text-emerald-400">
          <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
          ACTIVE
        </span>
      </div>

      {/* Quick Prompts Bar */}
      <div className="flex flex-wrap gap-1.5 border-b border-base-border/50 bg-base-card/40 px-3 py-1.5">
        {PROMPT_SUGGESTIONS.map((s) => (
          <button
            key={s}
            type="button"
            onClick={() => selectSuggestion(s)}
            className="rounded border border-base-border/70 bg-base-card px-2 py-0.5 text-[10px] text-slate-400 transition hover:border-emerald-500/40 hover:text-slate-200"
          >
            {s}
          </button>
        ))}
      </div>

      {/* Messages Feed */}
      <div ref={scrollRef} className="flex-1 space-y-3 overflow-y-auto px-3.5 py-3">
        {messages.length === 0 && !isLoading && (
          <div className="flex h-full flex-col items-center justify-center gap-2 text-center text-xs text-slate-500 px-4">
            <svg className="h-8 w-8 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <p>
              Ask FinAlly about your portfolio, request exposure analysis, or instruct it to execute orders directly.
            </p>
          </div>
        )}

        {messages.map((m) => (
          <div key={m.id} className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div
              className={`max-w-[88%] rounded-lg px-3.5 py-2.5 text-xs shadow-sm ${
                m.role === 'user'
                  ? 'border border-cyan-800/40 bg-cyan-950/40 text-slate-100'
                  : 'border border-base-border bg-base-card/90 text-slate-200'
              }`}
            >
              <div className="mb-1 flex items-center justify-between text-[10px] text-slate-400 font-mono">
                <span className="font-semibold uppercase tracking-wider">
                  {m.role === 'user' ? 'Trader' : 'Copilot'}
                </span>
                <span>
                  {m.created_at ? new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}
                </span>
              </div>

              <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>

              {m.actions && m.actions.length > 0 && (
                <div className="mt-2.5 space-y-1.5 border-t border-base-border/70 pt-2">
                  <div className="text-[10px] uppercase tracking-wider text-slate-400 font-mono">
                    Actions Executed
                  </div>
                  {m.actions.map((action, i) => (
                    <div
                      key={i}
                      className={`flex items-start gap-1.5 rounded px-2 py-1 text-[11px] font-mono ${
                        action.success
                          ? 'border border-emerald-900/50 bg-emerald-950/40 text-emerald-300'
                          : 'border border-rose-900/50 bg-rose-950/40 text-rose-300'
                      }`}
                    >
                      <span className="font-bold">{action.success ? '✓' : '✗'}</span>
                      <span>{action.detail}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}

        {isLoading && (
          <div className="flex justify-start">
            <div className="flex items-center gap-2 rounded-lg border border-base-border bg-base-card px-3 py-2 text-xs text-slate-400">
              <span className="h-2 w-2 rounded-full bg-emerald-400 animate-ping" />
              <span>Analyzing market data &amp; portfolio state…</span>
            </div>
          </div>
        )}
      </div>

      {/* Input Deck */}
      <div className="flex gap-2 border-t border-base-border p-3 bg-base-surface/50">
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Ask FinAlly to analyze risk or execute trades…"
          className="flex-1 rounded-md border border-base-border bg-base-card px-3 py-2 text-xs text-slate-200 outline-none transition focus:border-emerald-500/50"
        />
        <button
          type="button"
          onClick={submit}
          disabled={isLoading || !draft.trim()}
          className="flex items-center gap-1.5 rounded-md bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-sm transition hover:bg-emerald-500 active:scale-[0.98] disabled:opacity-40"
        >
          <span>Send</span>
          <svg className="h-3 w-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <line x1="22" y1="2" x2="11" y2="13" />
            <polygon points="22 2 15 22 11 13 2 9 22 2" />
          </svg>
        </button>
      </div>
    </section>
  );
}

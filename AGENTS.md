# FinAlly — Multi-Agent Engineering Guidelines & Invariants

## 1. System Vision & Boundaries
FinAlly (Finance Ally) is an AI-powered real-time trading workstation.
- Architecture: Single Docker container, single port 8000.
- Frontend: Next.js with TypeScript and Tailwind CSS, built as a static export (`output: 'export'`), served by FastAPI.
- Backend: FastAPI (Python), managed using `uv`.
- Persistence: SQLite database at `db/finally.db` with lazy initialization.
- Real-time stream: Server-Sent Events (SSE) at `/api/stream/prices`.
- AI integration: LiteLLM -> OpenRouter (Cerebras fast inference) with Structured Outputs for actions.

## 2. Invariants & Rules of Engineering
- Zero Placeholders: All live data must be calculated dynamically and updated in real-time.
- Zero Emojis: Strictly no emojis in UI headers, buttons, cards, status badges, empty states, code, or logs. Use clean SVG vector icons or semantic text.
- Tooling Standards: Always use `uv` for Python (`uv run`, `uv add`). Never call bare `python` or `pip`.
- Single Choke Point: All trade executions (manual from trade bar or AI-generated from chat) MUST go through `portfolio.trades.execute_trade()`. Never bypass trade validation.
- Atomicity: Trades execute within a single SQLite transaction updating cash, position, trade log, and portfolio snapshot.
- Fixed Ticker Universe: Tickers are strictly limited to the 10 supported symbols: AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX.
- In-Memory Price Cache: Live prices and short-term rolling history buffers are stored in memory and served via SSE/history endpoints. Prices are never written to SQLite.

## 3. Directory Layout
- `backend/`: FastAPI application (`app/market`, `app/db`, `app/portfolio`, `app/watchlist`, `app/chat`, `app/api`).
- `frontend/`: Next.js web application.
- `planning/`: Specification docs (`PLAN.md`, `ARCHITECTURE.md`, `MARKET_INTERFACE.md`, `MARKET_SIMULATOR.md`).
- `db/`: Volume-mounted SQLite database file `finally.db`.
- `scripts/`: Operational start/stop scripts.
- `.claude/`: Skills, sub-agents, and hooks.

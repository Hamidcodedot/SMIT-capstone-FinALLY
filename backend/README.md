# FinAlly Backend

FastAPI service powering the FinAlly Trading Workstation.
- Live market data generation (GBM simulator and Massive/Polygon interface)
- SSE price streaming at `/api/stream/prices`
- SQLite portfolio state and atomic trade execution at `/api/portfolio/trade`
- AI chat co-pilot with structured actions at `/api/chat`
- Static export serving on port 8000

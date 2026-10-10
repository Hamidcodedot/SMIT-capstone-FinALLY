from __future__ import annotations

import json
from ..db.connection import get_db
from ..market.cache import PriceCache
from ..portfolio.valuation import get_portfolio
from ..watchlist.service import get_watchlist


def get_chat_history(user_id: str = "default", limit: int = 10) -> list[dict]:
    """Retrieve the most recent chat messages for conversation context and UI reload."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, role, content, actions, created_at FROM chat_messages "
            "WHERE user_id = ? ORDER BY created_at DESC LIMIT ?",
            (user_id, limit),
        ).fetchall()

    messages = []
    for r in reversed(rows):
        actions_raw = r["actions"]
        actions = None
        if actions_raw:
            try:
                actions = json.loads(actions_raw)
            except Exception:
                actions = None
        messages.append({
            "id": r["id"],
            "role": r["role"],
            "content": r["content"],
            "actions": actions,
            "created_at": r["created_at"],
        })
    return messages


def build_system_prompt(cache: PriceCache, user_id: str = "default") -> str:
    """Build dynamic, live prompt grounding the LLM in real-time market and portfolio state."""
    portfolio = get_portfolio(cache, user_id=user_id)
    watchlist = get_watchlist(cache, user_id=user_id)

    holdings_lines = []
    if portfolio["positions"]:
        for pos in portfolio["positions"]:
            holdings_lines.append(
                f"- {pos['ticker']}: {pos['quantity']} shares, Avg Cost: ${pos['avg_cost']:.2f}, "
                f"Current Price: ${pos['current_price']:.2f}, Unrealized P&L: ${pos['unrealized_pnl']:.2f} "
                f"({pos['pnl_percent']:+.2f}%)"
            )
    else:
        holdings_lines.append("- No open positions (100% cash).")

    watchlist_lines = []
    for item in watchlist:
        p_str = f"${item['price']:.2f}" if item['price'] is not None else "N/A"
        cp_str = f"{item['change_percent']:+.2f}%" if item['change_percent'] is not None else "0.00%"
        watchlist_lines.append(f"- {item['ticker']}: {p_str} ({cp_str})")

    holdings_summary = "\n".join(holdings_lines)
    watchlist_summary = "\n".join(watchlist_lines)

    return f"""You are FinAlly, an elite AI Trading Assistant integrated into a real-time trading workstation.
Your role is to analyze portfolio composition, evaluate risk, provide data-backed market commentary, suggest trades with clear rationale, and execute trades or watchlist modifications on the user's behalf.

CURRENT LIVE PORTFOLIO STATE:
- Cash Balance: ${portfolio['cash_balance']:.2f}
- Total Portfolio Value: ${portfolio['total_value']:.2f}
- Total Unrealized P&L: ${portfolio['total_pnl']:.2f}

OPEN POSITIONS:
{holdings_summary}

CURRENT WATCHLIST & LIVE PRICES:
{watchlist_summary}

CORE OPERATIONAL INVARIANTS:
1. Supported Universe: Only 10 tickers exist in this system: AAPL, GOOGL, MSFT, AMZN, TSLA, NVDA, META, JPM, V, NFLX. Never attempt to trade or watch any other ticker.
2. Market Orders Only: All trades execute instantly at the live market price.
3. No Margin / Cash Invariant: Buying requires sufficient available cash.
4. No Short Selling: Selling requires holding at least the requested number of shares.
5. Absolute Zero Emoji Policy: Strictly do NOT use emojis in your response or messages. Keep tone analytical, concise, and professional.

RESPONSE FORMAT REQUIREMENTS:
You MUST respond with valid JSON strictly conforming to this schema:
{{
  "message": "Your conversational response to the user explaining your analysis or actions taken.",
  "trades": [
    {{"ticker": "SYMBOL", "side": "buy" or "sell", "quantity": 10.0}}
  ],
  "watchlist_changes": [
    {{"ticker": "SYMBOL", "action": "add" or "remove"}}
  ]
}}

If no trades are requested or agreed, set "trades": [].
If no watchlist modifications are requested or agreed, set "watchlist_changes": [].
Always output valid JSON only. Do not wrap in markdown code fences unless standard JSON string."""

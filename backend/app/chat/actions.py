from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any

from ..db.connection import get_db
from ..market.cache import PriceCache
from ..portfolio.trades import execute_trade
from ..watchlist.service import add_to_watchlist, remove_from_watchlist

logger = logging.getLogger(__name__)


def parse_llm_json_response(raw_text: str) -> dict[str, Any]:
    """Extract and parse structured JSON from model output, handling potential markdown blocks."""
    cleaned = raw_text.strip()
    # Check for markdown code blocks
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        cleaned = match.group(1).strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception as e:
        logger.warning("Failed direct JSON parse: %s. Attempting bracket extraction.", e)

    # Fallback: search for first '{' and last '}'
    first_brace = raw_text.find("{")
    last_brace = raw_text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        try:
            data = json.loads(raw_text[first_brace : last_brace + 1])
            if isinstance(data, dict):
                return data
        except Exception:
            pass

    # Safe fallback if output was plain text
    return {
        "message": raw_text.strip(),
        "trades": [],
        "watchlist_changes": [],
    }


def execute_llm_actions(
    cache: PriceCache,
    parsed_response: dict[str, Any],
    user_id: str = "default",
) -> list[dict]:
    """Execute trades and watchlist actions emitted by the LLM."""
    actions: list[dict] = []

    # 1. Execute trades
    trades = parsed_response.get("trades") or []
    for t in trades:
        if not isinstance(t, dict):
            continue
        ticker = str(t.get("ticker", "")).strip().upper()
        side = str(t.get("side", "")).strip().lower()
        try:
            quantity = float(t.get("quantity", 0))
        except (ValueError, TypeError):
            actions.append({
                "type": "trade",
                "detail": f"Invalid trade quantity for {ticker}",
                "success": False,
            })
            continue

        if not ticker or side not in ("buy", "sell") or quantity <= 0:
            continue

        try:
            result = execute_trade(cache, ticker, quantity, side, user_id=user_id)
            actions.append({
                "type": "trade",
                "detail": f"{side.upper()} {result['quantity']} {result['ticker']} @ ${result['price']:.2f}",
                "success": True,
            })
        except ValueError as err:
            actions.append({
                "type": "trade",
                "detail": f"Failed {side.upper()} {quantity} {ticker}: {err}",
                "success": False,
            })
        except Exception as err:
            logger.error("Unexpected error executing AI trade: %s", err)
            actions.append({
                "type": "trade",
                "detail": f"Failed {side.upper()} {quantity} {ticker}: System error",
                "success": False,
            })

    # 2. Execute watchlist changes
    wl_changes = parsed_response.get("watchlist_changes") or []
    for w in wl_changes:
        if not isinstance(w, dict):
            continue
        ticker = str(w.get("ticker", "")).strip().upper()
        action = str(w.get("action", "")).strip().lower()

        if action == "add":
            try:
                add_to_watchlist(ticker, cache, user_id=user_id)
                actions.append({
                    "type": "watchlist",
                    "detail": f"Added {ticker} to watchlist",
                    "success": True,
                })
            except ValueError as err:
                actions.append({
                    "type": "watchlist",
                    "detail": f"Could not add {ticker}: {err}",
                    "success": False,
                })
        elif action == "remove":
            try:
                remove_from_watchlist(ticker, user_id=user_id)
                actions.append({
                    "type": "watchlist",
                    "detail": f"Removed {ticker} from watchlist",
                    "success": True,
                })
            except Exception as err:
                actions.append({
                    "type": "watchlist",
                    "detail": f"Could not remove {ticker}: {err}",
                    "success": False,
                })

    return actions


def persist_chat_turn(
    user_content: str,
    assistant_content: str,
    actions: list[dict] | None,
    user_id: str = "default",
) -> dict:
    """Save both user message and assistant reply to SQLite and return the assistant ChatMessage payload."""
    now_iso = datetime.now(timezone.utc).isoformat()
    user_msg_id = str(uuid.uuid4())
    asst_msg_id = str(uuid.uuid4())

    with get_db() as conn:
        conn.execute(
            "INSERT INTO chat_messages (id, user_id, role, content, actions, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (user_msg_id, user_id, "user", user_content, None, now_iso),
        )

        actions_json = json.dumps(actions) if actions else None
        conn.execute(
            "INSERT INTO chat_messages (id, user_id, role, content, actions, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (asst_msg_id, user_id, "assistant", assistant_content, actions_json, now_iso),
        )

    return {
        "id": asst_msg_id,
        "role": "assistant",
        "content": assistant_content,
        "actions": actions if actions else None,
        "created_at": now_iso,
    }

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any

from ..market.cache import PriceCache
from ..market.types import TICKER_UNIVERSE
from .actions import execute_llm_actions, parse_llm_json_response, persist_chat_turn
from .context import build_system_prompt, get_chat_history

logger = logging.getLogger(__name__)


def _generate_mock_reply(
    user_message: str,
    cache: PriceCache,
    user_id: str = "default",
) -> dict[str, Any]:
    """Generate deterministic, context-aware mock responses for testing and zero-key environments."""
    lower_msg = user_message.lower()

    # Detect buy request
    buy_match = re.search(r"buy\s+(\d+(?:\.\d+)?)\s*(?:shares\s+of\s+)?([a-zA-Z]+)", lower_msg)
    if buy_match:
        qty = float(buy_match.group(1))
        ticker = buy_match.group(2).upper()
        if ticker in TICKER_UNIVERSE:
            return {
                "message": f"Executing market buy order for {qty} shares of {ticker} at current market price.",
                "trades": [{"ticker": ticker, "side": "buy", "quantity": qty}],
                "watchlist_changes": [],
            }

    # Detect sell request
    sell_match = re.search(r"sell\s+(\d+(?:\.\d+)?)\s*(?:shares\s+of\s+)?([a-zA-Z]+)", lower_msg)
    if sell_match:
        qty = float(sell_match.group(1))
        ticker = sell_match.group(2).upper()
        if ticker in TICKER_UNIVERSE:
            return {
                "message": f"Executing market sell order for {qty} shares of {ticker} at current market price.",
                "trades": [{"ticker": ticker, "side": "sell", "quantity": qty}],
                "watchlist_changes": [],
            }

    # Detect watchlist add
    add_match = re.search(r"add\s+([a-zA-Z]+)\s+to\s+watchlist", lower_msg)
    if add_match:
        ticker = add_match.group(1).upper()
        if ticker in TICKER_UNIVERSE:
            return {
                "message": f"Added {ticker} to your active watchlist.",
                "trades": [],
                "watchlist_changes": [{"ticker": ticker, "action": "add"}],
            }

    # Detect watchlist remove
    rem_match = re.search(r"remove\s+([a-zA-Z]+)\s+from\s+watchlist", lower_msg)
    if rem_match:
        ticker = rem_match.group(1).upper()
        if ticker in TICKER_UNIVERSE:
            return {
                "message": f"Removed {ticker} from your active watchlist.",
                "trades": [],
                "watchlist_changes": [{"ticker": ticker, "action": "remove"}],
            }

    # General analytical inquiry
    return {
        "message": (
            "FinAlly Copilot active. Your portfolio is monitored in real-time. "
            "You can ask me to evaluate risk exposure, suggest trades, or execute orders directly "
            "(e.g., 'buy 5 AAPL' or 'sell 2 MSFT')."
        ),
        "trades": [],
        "watchlist_changes": [],
    }


async def process_chat_message(
    user_content: str,
    cache: PriceCache,
    user_id: str = "default",
) -> dict:
    """Orchestrate LLM prompt construction, structured inference, action execution, and persistence."""
    api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
    is_mock = os.getenv("LLM_MOCK", "").lower() in ("true", "1", "yes") or not api_key

    parsed_output: dict[str, Any]

    if is_mock:
        logger.info("Using deterministic LLM mock mode")
        parsed_output = _generate_mock_reply(user_content, cache, user_id=user_id)
    else:
        system_prompt = build_system_prompt(cache, user_id=user_id)
        history = get_chat_history(user_id=user_id, limit=10)

        messages = [{"role": "system", "content": system_prompt}]
        for h in history:
            messages.append({"role": h["role"], "content": h["content"]})
        messages.append({"role": "user", "content": user_content})

        model_name = os.getenv("OPENROUTER_MODEL", "openrouter/openai/gpt-oss-120b")

        try:
            import litellm

            litellm.telemetry = False
            response = await litellm.acompletion(
                model=model_name,
                messages=messages,
                api_key=api_key,
                response_format={"type": "json_object"},
                temperature=0.2,
                extra_headers={
                    "HTTP-Referer": "http://localhost:8000",
                    "X-Title": "FinAlly Trading Bot",
                },
            )
            raw_content = response.choices[0].message.content or "{}"
            parsed_output = parse_llm_json_response(raw_content)
        except Exception as e:
            logger.error("LLM call failed (%s), falling back to analytical mock handler", e)
            parsed_output = _generate_mock_reply(user_content, cache, user_id=user_id)

    # Auto-execute trades and watchlist actions
    actions = execute_llm_actions(cache, parsed_output, user_id=user_id)
    assistant_msg = parsed_output.get("message", "Request processed.")

    # Persist both user and assistant turns
    return persist_chat_turn(
        user_content=user_content,
        assistant_content=assistant_msg,
        actions=actions,
        user_id=user_id,
    )

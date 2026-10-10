from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..chat.context import get_chat_history
from ..chat.llm import process_chat_message
from ..market.cache import PriceCache
from .deps import get_cache

router = APIRouter(tags=["AI Copilot"])


class ChatMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, description="User chat message content")


@router.get("/chat")
async def get_recent_chat():
    """Retrieve the recent chat conversation history."""
    return get_chat_history()


@router.post("/chat")
async def send_chat_message(
    req: ChatMessageRequest,
    cache: PriceCache = Depends(get_cache),
):
    """Process user message through AI Copilot, execute structured actions, and return response."""
    try:
        reply = await process_chat_message(req.content, cache)
        return reply
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {err}")

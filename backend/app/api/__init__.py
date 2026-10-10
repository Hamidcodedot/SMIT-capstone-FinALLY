from fastapi import APIRouter

from .chat import router as chat_router
from .health import router as health_router
from .portfolio import router as portfolio_router
from .prices import router as prices_router
from .watchlist import router as watchlist_router

api_router = APIRouter(prefix="/api")
api_router.include_router(prices_router)
api_router.include_router(portfolio_router)
api_router.include_router(watchlist_router)
api_router.include_router(chat_router)
api_router.include_router(health_router)

__all__ = ["api_router"]

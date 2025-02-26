from fastapi import APIRouter
from .trading import router as trading_router

# Create main router
router = APIRouter()

# Include trading routes with /trading prefix
router.include_router(trading_router, prefix="/trading")

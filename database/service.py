from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from contextlib import asynccontextmanager
from .models import Base, Trade, Order, Position
from core.config import settings
from core.logger import logger

# Create async engine with explicit driver
engine = create_async_engine(
    "postgresql+asyncpg://quantalgo:quantum123@localhost:5433/trading_bot_db",
    echo=True,
    future=True,
    pool_pre_ping=True,
    # Add explicit asyncpg driver settings
    connect_args={
        "server_settings": {
            "application_name": "QuantAlgoAI"
        }
    }
)

# Create async session factory
async_session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@asynccontextmanager
async def get_db() -> AsyncSession:
    """Get database session"""
    async with async_session() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            await session.close()

class DatabaseService:
    """Database operations service"""
    
    @staticmethod
    async def create_trade(trade_data: dict) -> Optional[Trade]:
        """Create new trade record"""
        try:
            async with get_db() as db:
                trade = Trade(**trade_data)
                db.add(trade)
                await db.commit()
                await db.refresh(trade)
                return trade
        except Exception as e:
            logger.error(f"Trade creation failed: {e}")
            return None 
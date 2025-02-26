from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Create the declarative base
Base = declarative_base()

# Create async engine with explicit asyncpg driver
engine = create_async_engine(
    "postgresql+asyncpg://quantalgo:quantum123@localhost:5433/trading_bot_db",
    echo=True,
    future=True,
    pool_pre_ping=True
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
) 
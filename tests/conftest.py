import sys
import os
from pathlib import Path
import numpy as np

# Add the project root directory to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)  # Insert at beginning of path

import pytest
import asyncio
from typing import AsyncGenerator, Dict
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Now import our modules
from database.models import Base
from core.config import settings

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_db_engine():
    """Create test database engine"""
    engine = create_async_engine(
        "postgresql+asyncpg://quantalgo:quantum123@localhost:5433/trading_bot_db",  # Note +asyncpg
        echo=True
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def test_db(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Get test database session"""
    async_session = sessionmaker(
        test_db_engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session

@pytest.fixture
def mock_broker():
    """Mock broker for testing"""
    class MockBroker:
        async def connect(self):
            return True
            
        async def place_order(self, order):
            return {"order_id": "test123", "status": "FILLED"}
            
        async def get_positions(self):
            return [{
                "symbol": "NIFTY",
                "quantity": 50,
                "average_price": 19500
            }]
    return MockBroker()

@pytest.fixture
def sample_market_data():
    return {
        "symbol": "NIFTY",
        "price": 19500,
        "timestamp": "2024-02-20T10:00:00",
        "volume": 100000
    }

class MockModel:
    def predict(self, X):
        return np.array([1])  # Return numpy array instead of list
    
    def predict_proba(self, X):
        return np.array([[0.3, 0.7]])  # Return numpy array instead of list 
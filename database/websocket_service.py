from typing import Dict, List, Optional
from datetime import datetime
import asyncpg
from core.logger import logger

class WebSocketDBService:
    """Database service for WebSocket data management"""
    
    def __init__(self, dsn: str):
        self.dsn = dsn
        self.pool = None

    async def init_pool(self):
        """Initialize connection pool"""
        try:
            self.pool = await asyncpg.create_pool(self.dsn)
            await self._create_tables()
            logger.info("WebSocket database service initialized")
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise

    async def _create_tables(self):
        """Create required tables if they don't exist"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS websocket_connections (
                    id SERIAL PRIMARY KEY,
                    connection_id TEXT UNIQUE NOT NULL,
                    status TEXT NOT NULL,
                    connected_at TIMESTAMP WITH TIME ZONE,
                    disconnected_at TIMESTAMP WITH TIME ZONE,
                    reconnect_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS market_data_subscriptions (
                    id SERIAL PRIMARY KEY,
                    connection_id TEXT REFERENCES websocket_connections(connection_id),
                    symbol TEXT NOT NULL,
                    exchange TEXT NOT NULL,
                    subscription_mode INTEGER NOT NULL,
                    subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    last_data_at TIMESTAMP WITH TIME ZONE,
                    status TEXT NOT NULL,
                    UNIQUE(connection_id, symbol, exchange)
                );

                CREATE TABLE IF NOT EXISTS connection_health_metrics (
                    id SERIAL PRIMARY KEY,
                    connection_id TEXT REFERENCES websocket_connections(connection_id),
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
                    connection_stability FLOAT,
                    data_coherence FLOAT,
                    latency INTEGER,
                    error_count INTEGER DEFAULT 0
                );
            """)

    async def log_connection(self, connection_id: str, status: str) -> None:
        """Log WebSocket connection status"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO websocket_connections (connection_id, status, connected_at)
                VALUES ($1, $2, CURRENT_TIMESTAMP)
                ON CONFLICT (connection_id) 
                DO UPDATE SET 
                    status = $2,
                    reconnect_count = websocket_connections.reconnect_count + 1
                    WHERE websocket_connections.status != $2
            """, connection_id, status)

    async def log_subscription(self, connection_id: str, symbol: str, 
                             exchange: str, mode: int) -> None:
        """Log market data subscription"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO market_data_subscriptions 
                (connection_id, symbol, exchange, subscription_mode, status)
                VALUES ($1, $2, $3, $4, 'active')
                ON CONFLICT (connection_id, symbol, exchange) 
                DO UPDATE SET 
                    subscription_mode = $4,
                    subscribed_at = CURRENT_TIMESTAMP,
                    status = 'active'
            """, connection_id, symbol, exchange, mode)

    async def update_health_metrics(self, connection_id: str, 
                                  metrics: Dict[str, float]) -> None:
        """Update connection health metrics"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO connection_health_metrics 
                (connection_id, connection_stability, data_coherence, latency)
                VALUES ($1, $2, $3, $4)
            """, connection_id, 
                metrics['connection_stability'],
                metrics['data_coherence'],
                metrics['latency'])

    async def get_connection_status(self, connection_id: str) -> Optional[Dict]:
        """Get current connection status and metrics"""
        async with self.pool.acquire() as conn:
            return await conn.fetchrow("""
                SELECT 
                    c.status,
                    c.connected_at,
                    c.reconnect_count,
                    h.connection_stability,
                    h.data_coherence,
                    h.latency
                FROM websocket_connections c
                LEFT JOIN connection_health_metrics h 
                    ON c.connection_id = h.connection_id
                WHERE c.connection_id = $1
                ORDER BY h.timestamp DESC
                LIMIT 1
            """, connection_id)

    async def get_active_subscriptions(self, connection_id: str) -> List[Dict]:
        """Get active market data subscriptions"""
        async with self.pool.acquire() as conn:
            return await conn.fetch("""
                SELECT symbol, exchange, subscription_mode, subscribed_at
                FROM market_data_subscriptions
                WHERE connection_id = $1 AND status = 'active'
            """, connection_id) 
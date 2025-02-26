from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from . import Base  # Import Base from the current package

class OrderStatus(enum.Enum):
    PENDING = "PENDING"
    OPEN = "OPEN"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"

class Trade(Base):
    __tablename__ = 'trades'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String)
    order_type = Column(String)
    quantity = Column(Integer)
    price = Column(Float)
    status = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    realized_pnl = Column(Float, nullable=True)
    stop_loss = Column(Float, nullable=True)
    take_profit = Column(Float, nullable=True)
    risk_amount = Column(Float, nullable=True)
    
    # Relationships
    orders = relationship("Order", back_populates="trade")
    position_id = Column(Integer, ForeignKey('positions.id'))
    position = relationship("Position", back_populates="trades")

class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float)
    order_type = Column(String)  # MARKET/LIMIT
    side = Column(String, nullable=False)  # BUY/SELL
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trade_id = Column(Integer, ForeignKey('trades.id'))
    trade = relationship("Trade", back_populates="orders")

class Position(Base):
    __tablename__ = 'positions'

    id = Column(Integer, primary_key=True)
    symbol = Column(String, nullable=False, unique=True)
    quantity = Column(Integer, default=0)
    average_price = Column(Float, default=0.0)
    current_price = Column(Float)
    unrealized_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    last_update = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    trades = relationship("Trade", back_populates="position")

class TradeStatus(enum.Enum):
    PENDING = "PENDING"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"

class TradeType(enum.Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"

class TradeModel(Base):
    __table_args__ = {'extend_existing': True}
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float)
    quantity = Column(Integer, nullable=False)
    side = Column(String(4), nullable=False)  # 'BUY' or 'SELL'
    status = Column(String(10), nullable=False)  # 'OPEN' or 'CLOSED'
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime)
    profit_loss = Column(Float)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Trade(symbol={self.symbol}, side={self.side}, status={self.status})>"

class MarketData(Base):
    __tablename__ = 'market_data'

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class TradingSession(Base):
    __tablename__ = 'trading_sessions'

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String)

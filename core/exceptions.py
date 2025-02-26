from typing import Optional, Dict, Any
from fastapi import HTTPException
from core.logger import logger

class TradingException(Exception):
    """Base exception for trading system"""
    def __init__(self, message: str, error_code: str, details: Optional[Dict] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)
        logger.error(f"Trading error: {self.message}", extra={
            "error_code": self.error_code,
            "details": self.details
        })

class OrderExecutionError(TradingException):
    """Order execution related errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "ORDER_EXECUTION_ERROR", details)

class MarketDataError(TradingException):
    """Market data related errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "MARKET_DATA_ERROR", details)

class ValidationError(TradingException):
    """Data validation errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_ERROR", details)

class RiskLimitError(TradingException):
    """Risk limit violation errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "RISK_LIMIT_ERROR", details)

class DatabaseError(TradingException):
    """Database operation errors"""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "DATABASE_ERROR", details) 
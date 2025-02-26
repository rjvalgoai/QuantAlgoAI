from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Union, Dict
from core.logger import logger

class ErrorHandler:
    """Global error handling middleware"""
    
    async def __call__(self, request: Request, call_next):
        try:
            return await call_next(request)
            
        except HTTPException as e:
            # Handle known HTTP exceptions
            return JSONResponse(
                status_code=e.status_code,
                content={"error": e.detail}
            )
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unhandled error: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"error": "Internal server error"}
            )
            
    async def handle_validation_error(self, exc) -> Dict:
        """Handle request validation errors"""
        return {
            "error": "Validation error",
            "details": [
                {
                    "field": err["loc"][-1],
                    "message": err["msg"]
                }
                for err in exc.errors()
            ]
        }
        
    async def handle_database_error(self, exc) -> Dict:
        """Handle database errors"""
        logger.error(f"Database error: {exc}")
        return {
            "error": "Database error",
            "message": str(exc)
        } 
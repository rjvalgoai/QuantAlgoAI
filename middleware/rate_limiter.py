# backend/middleware/rate_limiter.py
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
import time
from collections import defaultdict
from os import getenv

RATE_LIMIT = int(getenv("RATE_LIMIT_PER_MINUTE", 60))

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next):
        try:
            # Get client IP
            client_ip = request.client.host
            current_time = time.time()
            
            # Clean old requests
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if current_time - req_time < 60
            ]
            
            # Check if rate limit is exceeded
            if len(self.request_counts[client_ip]) >= self.requests_per_minute:
                raise HTTPException(
                    status_code=429,
                    detail="Rate limit exceeded. Please try again in a minute."
                )
            
            # Add current request
            self.request_counts[client_ip].append(current_time)
            
            # Process the request
            response = await call_next(request)
            return response
            
        except Exception as e:
            # Fallback behavior: allow the request if rate limiting fails
            return await call_next(request)
from fastapi.openapi.utils import get_openapi
from typing import Dict

def custom_openapi() -> Dict:
    """Generate custom OpenAPI documentation"""
    if app.openapi_schema:
        return app.openapi_schema
        
    openapi_schema = get_openapi(
        title="Quantitative Trading API",
        version="1.0.0",
        description="API for algorithmic trading system with ML and quantum computing capabilities",
        routes=app.routes,
    )
    
    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    
    # Add tags metadata
    openapi_schema["tags"] = [
        {
            "name": "trading",
            "description": "Trading operations endpoints"
        },
        {
            "name": "analysis",
            "description": "Market analysis endpoints"
        },
        {
            "name": "admin",
            "description": "System administration endpoints"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema 
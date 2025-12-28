"""Routes for LTrail API."""

from fastapi import APIRouter
from routes import traces, websocket, health, static

# Create main API router
api_router = APIRouter()

# Include all route modules (API routes first)
api_router.include_router(traces.router, prefix="/api", tags=["traces"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(health.router, prefix="/api", tags=["health"])

# Static router will be included separately in main.py to catch all non-API routes

__all__ = ["api_router", "static"]


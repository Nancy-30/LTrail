"""Routes for LTrail API."""

from fastapi import APIRouter
from routes import traces, websocket, health, static

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(traces.router, prefix="/api", tags=["traces"])
api_router.include_router(websocket.router, tags=["websocket"])
api_router.include_router(health.router, prefix="/api", tags=["health"])
api_router.include_router(static.router, tags=["static"])

__all__ = ["api_router"]


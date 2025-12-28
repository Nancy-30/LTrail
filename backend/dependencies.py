"""Shared dependencies for FastAPI routes."""

from services.storage import StorageService
from services.websocket_manager import WebSocketManager

# Global service instances (singletons)
# In production, use proper dependency injection container like FastAPI's lifespan events
storage_service = StorageService()
websocket_manager = WebSocketManager()


def get_storage() -> StorageService:
    """Get storage service instance."""
    return storage_service


def get_websocket_manager() -> WebSocketManager:
    """Get WebSocket manager instance."""
    return websocket_manager


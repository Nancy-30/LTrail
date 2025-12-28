"""Health check routes."""

from fastapi import APIRouter, Depends

from schemas.trace import HealthResponse
from dependencies import get_storage
from services.storage import StorageService

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check(storage: StorageService = Depends(get_storage)):
    """
    Health check endpoint.

    Args:
        storage: Storage service dependency

    Returns:
        HealthResponse with status and trace count
    """
    return {"status": "healthy", "traces_count": storage.get_trace_count()}

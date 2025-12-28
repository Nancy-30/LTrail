"""Static file serving routes."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path


router = APIRouter()

# Get static directory path
static_dir = Path(__file__).parent.parent / "static"


@router.get("/")
async def root():
    """
    Root endpoint - serve React app.

    Returns:
        index.html file for React SPA
    """
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {
        "message": "LTrail Backend API",
        "version": "1.0.0",
        "note": "Frontend not found",
    }


@router.get("/{full_path:path}")
async def serve_spa(full_path: str):
    """
    Serve React app for all non-API routes (SPA routing).

    This allows React Router to handle client-side routing.

    Args:
        full_path: Requested path

    Returns:
        index.html file for SPA routing

    Raises:
        HTTPException: If path is API route or frontend not found
    """
    # Don't serve index.html for API routes or WebSocket
    if (
        full_path.startswith("api/")
        or full_path.startswith("ws/")
        or full_path.startswith("static/")
    ):
        raise HTTPException(status_code=404, detail="Not found")

    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(status_code=404, detail="Frontend not found")

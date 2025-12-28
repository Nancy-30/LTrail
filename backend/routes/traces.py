"""Trace-related routes."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from schemas.trace import (
    TraceData,
    TraceResponse,
    StepUpdate,
    TraceListResponse,
    TraceCreateResponse,
    StepUpdateResponse,
)
from dependencies import get_storage, get_websocket_manager
from services.storage import StorageService
from services.websocket_manager import WebSocketManager

router = APIRouter()


@router.get("/traces", response_model=TraceListResponse)
async def get_traces(
    limit: int = 50, offset: int = 0, storage: StorageService = Depends(get_storage)
):
    """
    Get all traces with pagination.

    Args:
        limit: Maximum number of traces to return (default: 50)
        offset: Number of traces to skip (default: 0)
        storage: Storage service dependency

    Returns:
        TraceListResponse with traces and pagination info
    """
    return storage.get_all_traces(limit=limit, offset=offset)


@router.get("/traces/{trace_id}", response_model=TraceResponse)
async def get_trace(trace_id: str, storage: StorageService = Depends(get_storage)):
    """
    Get a specific trace by ID.

    Args:
        trace_id: Trace identifier
        storage: Storage service dependency

    Returns:
        TraceResponse with trace data and steps

    Raises:
        HTTPException: If trace not found
    """
    trace = storage.get_trace(trace_id)
    if trace is None:
        available_traces = list(storage.traces.keys())[:5]
        raise HTTPException(
            status_code=404,
            detail=f"Trace not found. Available traces: {available_traces}",
        )
    return trace


@router.post("/traces", response_model=TraceCreateResponse)
async def create_trace(
    trace_data: TraceData,
    storage: StorageService = Depends(get_storage),
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
):
    """
    Create or update a trace.

    Args:
        trace_data: Trace data from request body
        storage: Storage service dependency
        ws_manager: WebSocket manager dependency

    Returns:
        TraceCreateResponse with trace ID and status
    """
    trace_dict = trace_data.model_dump()
    created_trace = storage.create_trace(trace_dict)

    # Broadcast to WebSocket connections
    trace_with_steps = created_trace.copy()
    trace_with_steps["steps"] = storage.trace_steps.get(trace_data.trace_id, [])
    await ws_manager.broadcast_trace_update(
        trace_data.trace_id,
        {
            "type": "trace_updated",
            "trace": trace_with_steps,
            "steps": trace_dict.get("steps", []),
        },
    )

    return {"trace_id": trace_data.trace_id, "status": "created"}


@router.post("/traces/{trace_id}/steps", response_model=StepUpdateResponse)
async def add_step(
    trace_id: str,
    step_update: StepUpdate,
    storage: StorageService = Depends(get_storage),
    ws_manager: WebSocketManager = Depends(get_websocket_manager),
):
    """
    Add or update a step in a trace.

    Args:
        trace_id: Trace identifier from URL path
        step_update: Step update data from request body
        storage: Storage service dependency
        ws_manager: WebSocket manager dependency

    Returns:
        StepUpdateResponse with trace ID, step name, and status
    """
    # Validate trace_id matches
    if step_update.trace_id != trace_id:
        raise HTTPException(
            status_code=400,
            detail="Trace ID in URL does not match trace ID in request body",
        )

    step_data = step_update.step
    storage.add_step(trace_id, step_data)

    # Broadcast step update to WebSocket connections
    await ws_manager.broadcast_trace_update(
        trace_id, {"type": "step_updated", "trace_id": trace_id, "step": step_data}
    )

    return {
        "trace_id": trace_id,
        "step_name": step_data.get("name"),
        "status": "updated",
    }

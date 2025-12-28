"""FastAPI backend for LTrail dashboard."""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from collections import defaultdict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

app = FastAPI(title="LTrail Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (in production, use a database)
traces: Dict[str, Dict[str, Any]] = {}
trace_steps: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

# WebSocket connections for real-time updates
active_connections: Dict[str, List[WebSocket]] = defaultdict(list)


class TraceData(BaseModel):
    """Trace data model."""
    trace_id: str
    name: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: str
    steps: List[Dict[str, Any]]
    final_outcome: Optional[Dict[str, Any]] = None


class StepUpdate(BaseModel):
    """Step update model."""
    trace_id: str
    step: Dict[str, Any]


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "LTrail Backend API", "version": "1.0.0"}


@app.get("/api/traces")
async def get_traces(limit: int = 50, offset: int = 0):
    """Get all traces."""
    trace_list = list(traces.values())
    trace_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {
        "traces": trace_list[offset:offset + limit],
        "total": len(trace_list),
        "limit": limit,
        "offset": offset
    }


@app.get("/api/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Get a specific trace."""
    if trace_id not in traces:
        raise HTTPException(
            status_code=404, 
            detail=f"Trace not found. Available traces: {list(traces.keys())[:5]}"
        )
    
    trace = traces[trace_id].copy()
    trace["steps"] = trace_steps.get(trace_id, [])
    return trace


@app.post("/api/traces")
async def create_trace(trace_data: TraceData):
    """Create or update a trace."""
    trace_id = trace_data.trace_id
    
    # Store trace metadata
    traces[trace_id] = {
        "trace_id": trace_id,
        "name": trace_data.name,
        "metadata": trace_data.metadata or {},
        "created_at": trace_data.created_at,
        "final_outcome": trace_data.final_outcome,
        "status": "completed" if trace_data.final_outcome else "in_progress",
        "step_count": len(trace_data.steps)
    }
    
    # Store steps
    trace_steps[trace_id] = trace_data.steps
    
    # Broadcast to WebSocket connections
    trace_with_steps = traces[trace_id].copy()
    trace_with_steps["steps"] = trace_data.steps
    await broadcast_trace_update(trace_id, {
        "type": "trace_updated",
        "trace": trace_with_steps,
        "steps": trace_data.steps
    })
    
    return {"trace_id": trace_id, "status": "created"}


@app.post("/api/traces/{trace_id}/steps")
async def add_step(trace_id: str, step_update: StepUpdate):
    """Add or update a step in a trace."""
    if trace_id not in traces:
        # Create trace if it doesn't exist
        traces[trace_id] = {
            "trace_id": trace_id,
            "name": "Unknown",
            "metadata": {},
            "created_at": datetime.utcnow().isoformat() + "Z",
            "final_outcome": None,
            "status": "in_progress",
            "step_count": 0
        }
    
    step_data = step_update.step
    
    # Update or add step
    existing_steps = trace_steps[trace_id]
    step_name = step_data.get("name")
    
    # Check if step already exists
    step_index = next(
        (i for i, s in enumerate(existing_steps) if s.get("name") == step_name),
        None
    )
    
    if step_index is not None:
        existing_steps[step_index] = step_data
    else:
        existing_steps.append(step_data)
        traces[trace_id]["step_count"] = len(existing_steps)
    
    # Update trace status based on step status
    if step_data.get("status") == "error":
        traces[trace_id]["status"] = "error"
    
    # Broadcast step update to WebSocket connections
    await broadcast_trace_update(trace_id, {
        "type": "step_updated",
        "trace_id": trace_id,
        "step": step_data
    })
    
    return {"trace_id": trace_id, "step_name": step_name, "status": "updated"}


@app.websocket("/ws/{trace_id}")
async def websocket_endpoint(websocket: WebSocket, trace_id: str):
    """WebSocket endpoint for real-time trace updates."""
    await websocket.accept()
    active_connections[trace_id].append(websocket)
    
    try:
        # Send current trace state on connection
        if trace_id in traces:
            trace = traces[trace_id].copy()
            trace["steps"] = trace_steps.get(trace_id, [])
            await websocket.send_json({
                "type": "initial_state",
                "trace": trace,
                "steps": trace_steps.get(trace_id, [])
            })
        
        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket.send_json({"type": "pong", "data": data})
            
    except WebSocketDisconnect:
        active_connections[trace_id].remove(websocket)
        if not active_connections[trace_id]:
            del active_connections[trace_id]


async def broadcast_trace_update(trace_id: str, message: Dict[str, Any]):
    """Broadcast trace update to all connected WebSocket clients."""
    if trace_id in active_connections:
        disconnected = []
        for connection in active_connections[trace_id]:
            try:
                await connection.send_json(message)
            except:
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            active_connections[trace_id].remove(conn)


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "traces_count": len(traces)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


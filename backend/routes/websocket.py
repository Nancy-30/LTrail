"""WebSocket routes for real-time updates."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from dependencies import storage_service, websocket_manager

router = APIRouter()


@router.websocket("/ws/{trace_id}")
async def websocket_endpoint(websocket: WebSocket, trace_id: str):
    """
    WebSocket endpoint for real-time trace updates.

    Args:
        websocket: WebSocket connection
        trace_id: Trace identifier
    """
    await websocket_manager.connect(websocket, trace_id)

    try:
        # Send current trace state on connection
        if storage_service.trace_exists(trace_id):
            trace = storage_service.get_trace(trace_id)
            steps = storage_service.trace_steps.get(trace_id, [])
            await websocket_manager.send_initial_state(
                websocket, trace_id, trace, steps
            )

        # Keep connection alive and handle messages
        while True:
            data = await websocket.receive_text()
            # Echo back or handle client messages if needed
            await websocket.send_json({"type": "pong", "data": data})

    except WebSocketDisconnect:
        await websocket_manager.disconnect(websocket, trace_id)

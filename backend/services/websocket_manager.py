"""WebSocket manager for real-time trace updates."""

from typing import Dict, List, Any
from fastapi import WebSocket, WebSocketDisconnect


class WebSocketManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        """Initialize WebSocket manager."""
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, trace_id: str) -> None:
        """
        Connect a WebSocket client.

        Args:
            websocket: WebSocket connection
            trace_id: Trace identifier
        """
        await websocket.accept()
        if trace_id not in self.active_connections:
            self.active_connections[trace_id] = []
        self.active_connections[trace_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, trace_id: str) -> None:
        """
        Disconnect a WebSocket client.

        Args:
            websocket: WebSocket connection
            trace_id: Trace identifier
        """
        if trace_id in self.active_connections:
            try:
                self.active_connections[trace_id].remove(websocket)
                if not self.active_connections[trace_id]:
                    del self.active_connections[trace_id]
            except ValueError:
                pass  # WebSocket already removed

    async def send_initial_state(
        self,
        websocket: WebSocket,
        trace_id: str,
        trace: Dict[str, Any],
        steps: List[Dict[str, Any]],
    ) -> None:
        """
        Send initial trace state to a WebSocket client.

        Args:
            websocket: WebSocket connection
            trace_id: Trace identifier
            trace: Trace data
            steps: List of step data
        """
        await websocket.send_json(
            {"type": "initial_state", "trace": trace, "steps": steps}
        )

    async def broadcast_trace_update(
        self, trace_id: str, message: Dict[str, Any]
    ) -> None:
        """
        Broadcast trace update to all connected WebSocket clients for a trace.

        Args:
            trace_id: Trace identifier
            message: Message to broadcast
        """
        if trace_id not in self.active_connections:
            return

        disconnected = []
        for connection in self.active_connections[trace_id]:
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            try:
                self.active_connections[trace_id].remove(conn)
            except ValueError:
                pass

        # Clean up empty connection lists
        if not self.active_connections[trace_id]:
            del self.active_connections[trace_id]

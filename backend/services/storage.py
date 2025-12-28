"""Storage service for managing traces and steps."""

from typing import Dict, List, Any, Optional
from collections import defaultdict
from datetime import datetime


class StorageService:
    """In-memory storage service for traces and steps."""

    def __init__(self):
        """Initialize storage with empty dictionaries."""
        self.traces: Dict[str, Dict[str, Any]] = {}
        self.trace_steps: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def get_all_traces(self, limit: int = 50, offset: int = 0) -> Dict[str, Any]:
        """
        Get all traces with pagination.

        Args:
            limit: Maximum number of traces to return
            offset: Number of traces to skip

        Returns:
            Dictionary with traces, total, limit, and offset
        """
        trace_list = list(self.traces.values())
        trace_list.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return {
            "traces": trace_list[offset : offset + limit],
            "total": len(trace_list),
            "limit": limit,
            "offset": offset,
        }

    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific trace by ID.

        Args:
            trace_id: Trace identifier

        Returns:
            Trace dictionary with steps, or None if not found
        """
        if trace_id not in self.traces:
            return None

        trace = self.traces[trace_id].copy()
        trace["steps"] = self.trace_steps.get(trace_id, [])
        return trace

    def create_trace(self, trace_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update a trace.

        Args:
            trace_data: Trace data dictionary

        Returns:
            Created trace dictionary
        """
        trace_id = trace_data["trace_id"]

        # Store trace metadata
        self.traces[trace_id] = {
            "trace_id": trace_id,
            "name": trace_data["name"],
            "metadata": trace_data.get("metadata") or {},
            "created_at": trace_data["created_at"],
            "final_outcome": trace_data.get("final_outcome"),
            "status": "completed" if trace_data.get("final_outcome") else "in_progress",
            "step_count": len(trace_data.get("steps", [])),
        }

        # Store steps
        if "steps" in trace_data:
            self.trace_steps[trace_id] = trace_data["steps"]

        return self.traces[trace_id]

    def add_step(self, trace_id: str, step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add or update a step in a trace.

        Args:
            trace_id: Trace identifier
            step_data: Step data dictionary

        Returns:
            Updated step data
        """
        # Create trace if it doesn't exist
        if trace_id not in self.traces:
            self.traces[trace_id] = {
                "trace_id": trace_id,
                "name": "Unknown",
                "metadata": {},
                "created_at": datetime.utcnow().isoformat() + "Z",
                "final_outcome": None,
                "status": "in_progress",
                "step_count": 0,
            }

        # Update or add step
        existing_steps = self.trace_steps[trace_id]
        step_name = step_data.get("name")

        # Check if step already exists
        step_index = next(
            (i for i, s in enumerate(existing_steps) if s.get("name") == step_name),
            None,
        )

        if step_index is not None:
            existing_steps[step_index] = step_data
        else:
            existing_steps.append(step_data)
            self.traces[trace_id]["step_count"] = len(existing_steps)

        # Update trace status based on step status
        if step_data.get("status") == "error":
            self.traces[trace_id]["status"] = "error"

        return step_data

    def get_trace_count(self) -> int:
        """
        Get the total number of traces.

        Returns:
            Number of traces
        """
        return len(self.traces)

    def trace_exists(self, trace_id: str) -> bool:
        """
        Check if a trace exists.

        Args:
            trace_id: Trace identifier

        Returns:
            True if trace exists, False otherwise
        """
        return trace_id in self.traces

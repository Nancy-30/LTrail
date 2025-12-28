"""Core classes for LTrail SDK."""

import uuid
import time
from datetime import datetime
from typing import Any, Dict, List, Optional


class Evaluation:
    """Tracks individual item evaluations in filtering/ranking steps."""

    def __init__(self, item_id: str, label: str):
        """
        Initialize an evaluation.

        Args:
            item_id: Unique identifier for the item being evaluated
            label: Human-readable label for the item
        """
        self.item_id = item_id
        self.label = label
        self.checks: List[Dict[str, Any]] = []
        self.status = "PENDING"

    def add_check(self, name: str, passed: bool, detail: str) -> None:
        """
        Add a check result to this evaluation.

        Args:
            name: Name of the check (e.g., "price_range", "min_rating")
            passed: Whether the check passed
            detail: Human-readable detail about the check result
        """
        self.checks.append({"name": name, "passed": passed, "detail": detail})

    def set_status(self, status: str) -> None:
        """
        Set the overall status of this evaluation.

        Args:
            status: Status string (e.g., "PASSED", "FAILED", "QUALIFIED", "REJECTED")
        """
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert the evaluation to a dictionary."""
        return {
            "item_id": self.item_id,
            "label": self.label,
            "checks": self.checks,
            "status": self.status,
        }


class Step:
    """Represents a single step in the decision pipeline."""

    def __init__(self, name: str, step_type: str = "logic"):
        """
        Initialize a step.

        Args:
            name: Name of the step
            step_type: Type of step (e.g., "logic", "llm_call", "api_call")
        """
        self.name = name
        self.step_type = step_type
        self.input_data: Dict[str, Any] = {}
        self.output_data: Dict[str, Any] = {}
        self.reasoning = ""
        self.evaluations: List[Evaluation] = []
        self.start_time = time.time()
        self.duration: Optional[float] = None
        self.status = "success"

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - calculate duration and handle errors."""
        self.duration = time.time() - self.start_time
        if exc_type is not None:
            self.status = "error"
            # Store error information
            if exc_val is not None:
                self.output_data["error"] = {
                    "type": exc_type.__name__ if exc_type else "Unknown",
                    "message": str(exc_val)
                }
        return False  # Don't suppress exceptions

    def log_input(self, data: Dict[str, Any]) -> None:
        """
        Log input data for this step.

        Args:
            data: Dictionary of input data
        """
        self.input_data = data

    def log_output(self, data: Dict[str, Any]) -> None:
        """
        Log output data for this step.

        Args:
            data: Dictionary of output data
        """
        self.output_data = data

    def set_reasoning(self, text: str) -> None:
        """
        Set the reasoning for this step.

        Args:
            text: Human-readable reasoning text
        """
        self.reasoning = text

    def set_status(self, status: str) -> None:
        """
        Set the status of this step.

        Args:
            status: Status string (e.g., "success", "error", "warning", "partial")
        """
        self.status = status

    def add_evaluation(self, item_id: str, label: str) -> Evaluation:
        """
        Add an evaluation for an item.

        Args:
            item_id: Unique identifier for the item
            label: Human-readable label for the item

        Returns:
            Evaluation object that can be used to add checks
        """
        evaluation = Evaluation(item_id, label)
        self.evaluations.append(evaluation)
        return evaluation

    def to_dict(self) -> Dict[str, Any]:
        """Convert the step to a dictionary."""
        result = {
            "name": self.name,
            "step_type": self.step_type,
            "input": self.input_data,
            "output": self.output_data,
            "reasoning": self.reasoning,
            "status": self.status,
            "evaluations": [e.to_dict() for e in self.evaluations],
        }
        if self.duration is not None:
            result["duration"] = self.duration
        return result


class LTrail:
    """Main orchestrator for traces."""

    def __init__(self, trace_name: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize a new trace.

        Args:
            trace_name: Name of the trace
            metadata: Optional metadata dictionary
        """
        self.trace_id = str(uuid.uuid4())
        self.trace_name = trace_name
        self.metadata = metadata or {}
        self.steps: List[Step] = []
        self.final_outcome: Optional[Dict[str, Any]] = None
        self.created_at = datetime.utcnow().isoformat() + "Z"

    @staticmethod
    def start_trace(
        name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> "LTrail":
        """
        Start a new trace (static factory method).

        Args:
            name: Name of the trace
            metadata: Optional metadata dictionary

        Returns:
            New LTrail instance
        """
        return LTrail(name, metadata)

    def step(self, name: str, step_type: str = "logic") -> Step:
        """
        Create a new step in the trace.

        Args:
            name: Name of the step
            step_type: Type of step (e.g., "logic", "llm_call", "api_call")

        Returns:
            Step object (context manager)
        """
        new_step = Step(name, step_type)
        self.steps.append(new_step)
        return new_step

    def complete(self, final_output: Optional[Any] = None) -> None:
        """
        Mark the trace as complete and optionally set final outcome.

        Args:
            final_output: Optional final output to store
        """
        if final_output is not None:
            if isinstance(final_output, dict):
                self.final_outcome = final_output
            else:
                self.final_outcome = {"result": final_output}

    def export(self) -> Dict[str, Any]:
        """
        Export the trace to a dictionary.

        Returns:
            Dictionary representation of the trace
        """
        return {
            "trace_id": self.trace_id,
            "name": self.trace_name,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "steps": [step.to_dict() for step in self.steps],
            "final_outcome": self.final_outcome,
        }


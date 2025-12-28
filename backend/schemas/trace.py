"""Pydantic schemas for trace-related endpoints."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class StepData(BaseModel):
    """Step data model."""

    name: str
    step_type: str
    status: str = "success"
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    reasoning: Optional[str] = None
    duration: Optional[float] = None
    evaluations: Optional[List[Dict[str, Any]]] = None


class TraceData(BaseModel):
    """Trace data model for creating/updating traces."""

    trace_id: str = Field(..., description="Unique trace identifier")
    name: str = Field(..., description="Trace name")
    metadata: Optional[Dict[str, Any]] = Field(
        default=None, description="Trace metadata"
    )
    created_at: str = Field(..., description="ISO format creation timestamp")
    steps: List[Dict[str, Any]] = Field(
        default_factory=list, description="List of step data"
    )
    final_outcome: Optional[Dict[str, Any]] = Field(
        default=None, description="Final outcome of the trace"
    )


class StepUpdate(BaseModel):
    """Step update model."""

    trace_id: str = Field(..., description="Trace ID to update")
    step: Dict[str, Any] = Field(..., description="Step data dictionary")


class TraceResponse(BaseModel):
    """Trace response model."""

    trace_id: str
    name: str
    metadata: Dict[str, Any]
    created_at: str
    status: str
    step_count: int
    final_outcome: Optional[Dict[str, Any]] = None
    steps: List[Dict[str, Any]] = Field(default_factory=list)


class TraceListResponse(BaseModel):
    """Response model for trace list endpoint."""

    traces: List[Dict[str, Any]] = Field(..., description="List of traces")
    total: int = Field(..., description="Total number of traces")
    limit: int = Field(..., description="Limit parameter used")
    offset: int = Field(..., description="Offset parameter used")


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = Field(..., description="Health status")
    traces_count: int = Field(..., description="Number of traces in storage")


class TraceCreateResponse(BaseModel):
    """Response model for trace creation."""

    trace_id: str = Field(..., description="Created trace ID")
    status: str = Field(..., description="Creation status")


class StepUpdateResponse(BaseModel):
    """Response model for step update."""

    trace_id: str = Field(..., description="Trace ID")
    step_name: Optional[str] = Field(None, description="Step name")
    status: str = Field(..., description="Update status")

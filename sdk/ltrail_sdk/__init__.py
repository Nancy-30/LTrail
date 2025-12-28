"""
LTrail SDK - A library for debugging multi-step algorithmic systems.

LTrail provides transparency into decision processes by capturing
decision context at each step: inputs, candidates, filters applied,
outcomes, and reasoning.
"""

from ltrail_sdk.core import LTrail, Step, Evaluation
from ltrail_sdk.storage import JSONFileStorage
from ltrail_sdk.backend_client import BackendClient, BackendStorage
from ltrail_sdk.exceptions import LTrailError, StepError, StorageError

__version__ = "0.1.0"

__all__ = [
    "LTrail",
    "Step",
    "Evaluation",
    "JSONFileStorage",
    "BackendClient",
    "BackendStorage",
    "LTrailError",
    "StepError",
    "StorageError",
]


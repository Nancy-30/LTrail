"""Custom exceptions for LTrail SDK."""


class LTrailError(Exception):
    """Base exception for all LTrail errors."""

    pass


class StepError(LTrailError):
    """Raised when there's an error with a step operation."""

    pass


class StorageError(LTrailError):
    """Raised when there's an error with storage operations."""

    pass


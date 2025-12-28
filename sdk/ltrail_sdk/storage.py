"""Storage backend for LTrail SDK."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from ltrail_sdk.core import LTrail
from ltrail_sdk.exceptions import StorageError


class JSONFileStorage:
    """Handles persistence of traces to JSON files."""

    def __init__(self, output_dir: str = "traces"):
        """
        Initialize JSON file storage.

        Args:
            output_dir: Directory where trace files will be saved
        """
        self.output_dir = Path(output_dir)

    def save_trace(self, ltrail_instance: LTrail, output_dir: Optional[str] = None) -> str:
        """
        Save a trace to a JSON file.

        Args:
            ltrail_instance: LTrail instance to save
            output_dir: Optional override for output directory

        Returns:
            Path to the saved file

        Raises:
            StorageError: If the file cannot be written
        """
        if output_dir is not None:
            save_dir = Path(output_dir)
        else:
            save_dir = self.output_dir

        # Ensure directory exists
        try:
            save_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            raise StorageError(f"Failed to create output directory: {e}") from e

        # Generate filename with timestamp
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"trace_{ltrail_instance.trace_id}_{timestamp}.json"
        filepath = save_dir / filename

        # Export trace data
        trace_data = ltrail_instance.export()

        # Write to file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(trace_data, f, indent=2, ensure_ascii=False)
        except (OSError, IOError) as e:
            raise StorageError(f"Failed to write trace file: {e}") from e

        return str(filepath)


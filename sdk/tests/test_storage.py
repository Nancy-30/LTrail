"""Unit tests for storage backend."""

import json
import os
import tempfile
from pathlib import Path

import pytest
from ltrail_sdk.core import LTrail
from ltrail_sdk.exceptions import StorageError
from ltrail_sdk.storage import JSONFileStorage


class TestJSONFileStorage:
    """Tests for JSONFileStorage class."""

    def test_storage_creation(self):
        """Test creating storage instance."""
        storage = JSONFileStorage("test_traces")
        assert storage.output_dir == Path("test_traces")

    def test_save_trace(self):
        """Test saving a trace to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JSONFileStorage(output_dir=tmpdir)
            ltrail = LTrail("Test Trace", {"key": "value"})
            with ltrail.step("test_step") as step:
                step.log_input({"input": "data"})
                step.log_output({"output": "data"})

            filepath = storage.save_trace(ltrail)
            assert os.path.exists(filepath)
            assert filepath.startswith(tmpdir)
            assert "trace_" in filepath
            assert ltrail.trace_id in filepath
            assert filepath.endswith(".json")

    def test_save_trace_creates_directory(self):
        """Test that save_trace creates directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            new_dir = os.path.join(tmpdir, "new_traces")
            storage = JSONFileStorage(output_dir=new_dir)
            ltrail = LTrail("Test Trace")

            filepath = storage.save_trace(ltrail)
            assert os.path.exists(new_dir)
            assert os.path.exists(filepath)

    def test_save_trace_custom_output_dir(self):
        """Test saving with custom output directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JSONFileStorage(output_dir="default")
            ltrail = LTrail("Test Trace")
            custom_dir = os.path.join(tmpdir, "custom")

            filepath = storage.save_trace(ltrail, output_dir=custom_dir)
            assert filepath.startswith(custom_dir)
            assert os.path.exists(custom_dir)

    def test_save_trace_file_content(self):
        """Test that saved file contains correct JSON structure."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JSONFileStorage(output_dir=tmpdir)
            ltrail = LTrail("Test Trace", {"key": "value"})
            with ltrail.step("test_step") as step:
                step.log_input({"input": "data"})
                step.log_output({"output": "data"})
            ltrail.complete({"result": "success"})

            filepath = storage.save_trace(ltrail)

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert data["name"] == "Test Trace"
            assert data["metadata"] == {"key": "value"}
            assert data["trace_id"] == ltrail.trace_id
            assert len(data["steps"]) == 1
            assert data["final_outcome"] == {"result": "success"}
            assert "created_at" in data

    def test_save_trace_with_evaluations(self):
        """Test saving trace with evaluations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            storage = JSONFileStorage(output_dir=tmpdir)
            ltrail = LTrail("Test Trace")
            with ltrail.step("filter_step") as step:
                eval = step.add_evaluation("item_123", "Test Item")
                eval.add_check("price_check", True, "$50 is valid")
                eval.set_status("QUALIFIED")

            filepath = storage.save_trace(ltrail)

            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            assert len(data["steps"]) == 1
            assert len(data["steps"][0]["evaluations"]) == 1
            eval_data = data["steps"][0]["evaluations"][0]
            assert eval_data["item_id"] == "item_123"
            assert eval_data["status"] == "QUALIFIED"
            assert len(eval_data["checks"]) == 1


"""Unit tests for core LTrail classes."""

import pytest
from ltrail_sdk.core import LTrail, Step, Evaluation


class TestEvaluation:
    """Tests for Evaluation class."""

    def test_evaluation_creation(self):
        """Test creating an evaluation."""
        eval = Evaluation("item_123", "Test Item")
        assert eval.item_id == "item_123"
        assert eval.label == "Test Item"
        assert eval.checks == []
        assert eval.status == "PENDING"

    def test_add_check(self):
        """Test adding checks to an evaluation."""
        eval = Evaluation("item_123", "Test Item")
        eval.add_check("price_check", True, "$50 is within range")
        eval.add_check("rating_check", False, "3.2 < 3.8 threshold")

        assert len(eval.checks) == 2
        assert eval.checks[0]["name"] == "price_check"
        assert eval.checks[0]["passed"] is True
        assert eval.checks[1]["passed"] is False

    def test_set_status(self):
        """Test setting evaluation status."""
        eval = Evaluation("item_123", "Test Item")
        eval.set_status("QUALIFIED")
        assert eval.status == "QUALIFIED"

    def test_to_dict(self):
        """Test converting evaluation to dictionary."""
        eval = Evaluation("item_123", "Test Item")
        eval.add_check("test_check", True, "Test detail")
        eval.set_status("PASSED")

        result = eval.to_dict()
        assert result["item_id"] == "item_123"
        assert result["label"] == "Test Item"
        assert result["status"] == "PASSED"
        assert len(result["checks"]) == 1


class TestStep:
    """Tests for Step class."""

    def test_step_creation(self):
        """Test creating a step."""
        step = Step("test_step", "logic")
        assert step.name == "test_step"
        assert step.step_type == "logic"
        assert step.input_data == {}
        assert step.output_data == {}
        assert step.reasoning == ""
        assert step.evaluations == []
        assert step.status == "success"

    def test_context_manager(self):
        """Test step as context manager."""
        with Step("test_step") as step:
            assert step is not None
            assert step.duration is None

        assert step.duration is not None
        assert step.duration > 0

    def test_log_input_output(self):
        """Test logging input and output."""
        step = Step("test_step")
        step.log_input({"count": 50})
        step.log_output({"filtered": 12})

        assert step.input_data == {"count": 50}
        assert step.output_data == {"filtered": 12}

    def test_set_reasoning(self):
        """Test setting reasoning."""
        step = Step("test_step")
        step.set_reasoning("Test reasoning")
        assert step.reasoning == "Test reasoning"

    def test_add_evaluation(self):
        """Test adding evaluations."""
        step = Step("test_step")
        eval = step.add_evaluation("item_123", "Test Item")

        assert len(step.evaluations) == 1
        assert eval.item_id == "item_123"
        assert eval.label == "Test Item"

    def test_to_dict(self):
        """Test converting step to dictionary."""
        step = Step("test_step", "logic")
        step.log_input({"input": "data"})
        step.log_output({"output": "data"})
        step.set_reasoning("Test reasoning")
        step.add_evaluation("item_123", "Test Item")

        result = step.to_dict()
        assert result["name"] == "test_step"
        assert result["step_type"] == "logic"
        assert result["input"] == {"input": "data"}
        assert result["output"] == {"output": "data"}
        assert result["reasoning"] == "Test reasoning"
        assert len(result["evaluations"]) == 1


class TestLTrail:
    """Tests for LTrail class."""

    def test_ltrail_creation(self):
        """Test creating a trace."""
        ltrail = LTrail("Test Trace", {"key": "value"})
        assert ltrail.trace_name == "Test Trace"
        assert ltrail.metadata == {"key": "value"}
        assert ltrail.steps == []
        assert ltrail.final_outcome is None
        assert ltrail.trace_id is not None

    def test_start_trace_static(self):
        """Test static factory method."""
        ltrail = LTrail.start_trace("Test Trace", {"key": "value"})
        assert isinstance(ltrail, LTrail)
        assert ltrail.trace_name == "Test Trace"
        assert ltrail.metadata == {"key": "value"}

    def test_add_step(self):
        """Test adding steps to a trace."""
        ltrail = LTrail("Test Trace")
        step = ltrail.step("test_step", "logic")

        assert len(ltrail.steps) == 1
        assert step.name == "test_step"
        assert step.step_type == "logic"

    def test_complete_with_dict(self):
        """Test completing trace with dictionary output."""
        ltrail = LTrail("Test Trace")
        ltrail.complete({"result": "success"})
        assert ltrail.final_outcome == {"result": "success"}

    def test_complete_with_non_dict(self):
        """Test completing trace with non-dict output."""
        ltrail = LTrail("Test Trace")
        ltrail.complete("success")
        assert ltrail.final_outcome == {"result": "success"}

    def test_export(self):
        """Test exporting trace to dictionary."""
        ltrail = LTrail("Test Trace", {"key": "value"})
        with ltrail.step("test_step") as step:
            step.log_input({"input": "data"})
            step.log_output({"output": "data"})

        result = ltrail.export()
        assert result["name"] == "Test Trace"
        assert result["metadata"] == {"key": "value"}
        assert result["trace_id"] == ltrail.trace_id
        assert len(result["steps"]) == 1
        assert "created_at" in result


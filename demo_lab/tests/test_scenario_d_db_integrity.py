import pytest
from demo_lab.app.scenarios import TracePointLab

def test_scenario_d_reproduces_orphaned_records_on_constraint_violation():
    """Confirms that the buggy batch runner leaves partial records committed when an integrity violation occurs."""
    res = TracePointLab.execute_batch_settlement(mode="buggy")
    assert res["defect_observed"] is True
    assert res["committed_lines_count"] > 0
    assert "Foreign Key Violation" in res["error_captured"]

def test_scenario_d_verifies_atomic_rollback():
    """Confirms that explicit transactional handling rolls back the entire batch, leaving 0 orphaned rows."""
    res = TracePointLab.execute_batch_settlement(mode="fixed")
    assert res["defect_observed"] is False
    assert res["is_clean_rollback"] is True
    assert res["committed_lines_count"] == 0
    assert "Foreign Key Violation" in res["error_captured"]

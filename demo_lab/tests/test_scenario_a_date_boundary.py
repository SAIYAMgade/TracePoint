import pytest
from demo_lab.app.scenarios import TracePointLab

def test_scenario_a_reproduces_defect_in_buggy_mode():
    """Confirms that the buggy query omits the midnight boundary record TXN-3 ($48,200)."""
    res = TracePointLab.calculate_revenue_date_boundary(
        start_date="2026-09-01",
        end_date="2026-09-30",
        mode="buggy"
    )
    assert res["defect_observed"] is True
    assert res["total_revenue"] == 26800.0  # Missing $48,200!
    assert len(res["included_transactions"]) == 2

def test_scenario_a_verifies_fix():
    """Confirms that the corrected date boundary logic captures all boundary transactions through 23:59:59."""
    res = TracePointLab.calculate_revenue_date_boundary(
        start_date="2026-09-01",
        end_date="2026-09-30",
        mode="fixed"
    )
    assert res["defect_observed"] is False
    assert res["is_accurate"] is True
    assert res["total_revenue"] == 75000.0
    assert len(res["included_transactions"]) == 3
    # Check that TXN-3 is included
    txn_ids = [t["txn_id"] for t in res["included_transactions"]]
    assert "TXN-3" in txn_ids

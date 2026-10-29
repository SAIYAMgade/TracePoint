import pytest
from demo_lab.app.scenarios import TracePointLab

def test_scenario_b_reproduces_cartesian_fan_out_defect():
    """Confirms that joining items with shipments without grouping multiplies total sales."""
    res = TracePointLab.calculate_order_summary(order_id="ORD-99", mode="buggy")
    assert res["defect_observed"] is True
    assert res["reported_total"] == 60000.0  # 3x inflated
    assert res["rows_aggregated"] == 6

def test_scenario_b_verifies_cte_grouping_fix():
    """Confirms that the corrected query produces the exact true order total."""
    res = TracePointLab.calculate_order_summary(order_id="ORD-99", mode="fixed")
    assert res["defect_observed"] is False
    assert res["is_accurate"] is True
    assert res["reported_total"] == 20000.0
    assert res["rows_aggregated"] == 2

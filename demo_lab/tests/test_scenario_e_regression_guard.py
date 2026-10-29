import pytest
from demo_lab.app.scenarios import TracePointLab

def test_scenario_e_reproduces_expired_coupon_regression():
    """Confirms that the buggy optimization accidentally accepted an expired coupon."""
    res = TracePointLab.calculate_discount(
        order_amount=100.0,
        coupon_code="SUMMER20",
        coupon_expiry_date="2026-06-01",
        mode="buggy"
    )
    assert res["defect_observed"] is True
    assert res["coupon_applied"] is True
    assert res["final_total"] == 80.0  # Discount incorrectly granted

def test_scenario_e_regression_guard_verifies_rejection():
    """Confirms that the regression guard rejects expired coupons."""
    res = TracePointLab.calculate_discount(
        order_amount=100.0,
        coupon_code="SUMMER20",
        coupon_expiry_date="2026-06-01",
        mode="fixed"
    )
    assert res["defect_observed"] is False
    assert res["coupon_applied"] is False
    assert res["discount_amount"] == 0.0
    assert res["final_total"] == 100.0

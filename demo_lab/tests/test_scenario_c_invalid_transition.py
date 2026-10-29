import pytest
from demo_lab.app.scenarios import TracePointLab

def test_scenario_c_reproduces_invalid_transition_defect():
    """Confirms that the unvalidated endpoint allows transitioning high-value invoices directly to ISSUED."""
    res = TracePointLab.process_invoice_transition(
        current_status="DRAFT",
        target_status="ISSUED",
        amount=75000.0,
        credit_approved=False,
        mode="buggy"
    )
    assert res["defect_observed"] is True
    assert res["result_status"] == "ISSUED"

def test_scenario_c_verifies_transition_guard():
    """Confirms that the corrected state guard blocks direct transition when credit is unapproved."""
    res = TracePointLab.process_invoice_transition(
        current_status="DRAFT",
        target_status="ISSUED",
        amount=75000.0,
        credit_approved=False,
        mode="fixed"
    )
    assert res["defect_observed"] is False
    assert res["transition_allowed"] is False
    assert res["result_status"] == "DRAFT"
    assert "require CREDIT_APPROVED" in res["message"]

def test_scenario_c_permits_valid_transition_with_approval():
    """Confirms that the transition is allowed when credit has been approved."""
    res = TracePointLab.process_invoice_transition(
        current_status="DRAFT",
        target_status="ISSUED",
        amount=75000.0,
        credit_approved=True,
        mode="fixed"
    )
    assert res["transition_allowed"] is True
    assert res["result_status"] == "ISSUED"

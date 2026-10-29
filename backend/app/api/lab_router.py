from fastapi import APIRouter, Query, Body
from typing import Dict, Any, Optional

from demo_lab.app.scenarios import TracePointLab

router = APIRouter(prefix="/lab", tags=["TracePoint Lab Demonstration Service"])

@router.get("/scenarios/date-boundary")
def run_scenario_a(
    start: str = Query("2026-09-01"),
    end: str = Query("2026-09-30"),
    mode: str = Query("buggy", pattern="^(buggy|fixed)$")
):
    return TracePointLab.calculate_revenue_date_boundary(start, end, mode)

@router.get("/scenarios/duplicate-aggregation")
def run_scenario_b(
    order_id: str = Query("ORD-99"),
    mode: str = Query("buggy", pattern="^(buggy|fixed)$")
):
    return TracePointLab.calculate_order_summary(order_id, mode)

@router.post("/scenarios/invoice-transition")
def run_scenario_c(
    current_status: str = Body("DRAFT"),
    target_status: str = Body("ISSUED"),
    amount: float = Body(75000.0),
    credit_approved: bool = Body(False),
    mode: str = Body("buggy")
):
    return TracePointLab.process_invoice_transition(
        current_status=current_status,
        target_status=target_status,
        amount=amount,
        credit_approved=credit_approved,
        mode=mode
    )

@router.post("/scenarios/batch-settlement")
def run_scenario_d(
    mode: str = Query("buggy", pattern="^(buggy|fixed)$")
):
    return TracePointLab.execute_batch_settlement(mode)

@router.post("/scenarios/discount-calculation")
def run_scenario_e(
    order_amount: float = Body(100.0),
    coupon_code: str = Body("SUMMER20"),
    coupon_expiry_date: str = Body("2026-06-01"),
    mode: str = Body("buggy")
):
    return TracePointLab.calculate_discount(
        order_amount=order_amount,
        coupon_code=coupon_code,
        coupon_expiry_date=coupon_expiry_date,
        mode=mode
    )

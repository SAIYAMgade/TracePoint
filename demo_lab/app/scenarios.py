import json
from datetime import datetime
from typing import Dict, Any, List, Optional
import sqlite3

class TracePointLab:
    """
    Controlled synthetic environment demonstrating realistic defects,
    root-cause investigations, and automated regression test validations.
    """

    # SCENARIO A: Date Boundary Calculation
    @staticmethod
    def calculate_revenue_date_boundary(start_date: str, end_date: str, mode: str = "buggy") -> Dict[str, Any]:
        """
        Fixtures:
        - TXN-1: 2026-09-15 10:00:00 -> $12,500
        - TXN-2: 2026-09-28 16:30:00 -> $14,300
        - TXN-3: 2026-09-30 23:55:00 -> $48,200 (Midnight boundary record)
        """
        records = [
            {"txn_id": "TXN-1", "timestamp": "2026-09-15 10:00:00", "amount": 12500.0},
            {"txn_id": "TXN-2", "timestamp": "2026-09-28 16:30:00", "amount": 14300.0},
            {"txn_id": "TXN-3", "timestamp": "2026-09-30 23:55:00", "amount": 48200.0},
        ]

        if mode == "buggy":
            # Bug: end_date string "2026-09-30" is compared directly with ISO timestamp
            # "2026-09-30 23:55:00" < "2026-09-30" evaluates to FALSE, dropping TXN-3!
            included = [
                r for r in records
                if r["timestamp"] >= start_date and r["timestamp"] < end_date
            ]
        else:
            # Fixed: end_date is treated as closed day boundary (until 23:59:59.999)
            end_boundary = f"{end_date} 23:59:59"
            included = [
                r for r in records
                if r["timestamp"] >= start_date and r["timestamp"] <= end_boundary
            ]

        total = sum(r["amount"] for r in included)
        return {
            "scenario": "Scenario A: Date Boundary Handling",
            "mode": mode,
            "filter_start": start_date,
            "filter_end": end_date,
            "included_transactions": included,
            "total_revenue": total,
            "expected_revenue": 75000.0,
            "is_accurate": (total == 75000.0),
            "defect_observed": (total < 75000.0),
            "explanation": "Buggy mode drops boundary transaction TXN-3 ($48,200) because string comparison treats end_date as midnight 00:00:00." if mode == "buggy" else "Fixed mode correctly encompasses all transactions through end-of-day."
        }

    # SCENARIO B: Duplicate Aggregate Results (Cartesian Fan-Out)
    @staticmethod
    def calculate_order_summary(order_id: str = "ORD-99", mode: str = "buggy") -> Dict[str, Any]:
        """
        Fixtures:
        Order ORD-99 has 2 items:
          - Line 1: Server Blade ($5,000)
          - Line 2: SAN Storage ($15,000)
        Actual total = $20,000.

        Order was split into 3 partial shipments (Shipment 1, Shipment 2, Shipment 3).
        """
        items = [
            {"line_id": "L1", "desc": "Server Blade", "amount": 5000.0},
            {"line_id": "L2", "desc": "SAN Storage", "amount": 15000.0}
        ]
        shipments = [
            {"shipment_id": "SH-101", "tracking": "TRK-A"},
            {"shipment_id": "SH-102", "tracking": "TRK-B"},
            {"shipment_id": "SH-103", "tracking": "TRK-C"}
        ]

        if mode == "buggy":
            # Bug: Joining items to shipments without grouping line items first
            # 2 items * 3 shipments = 6 joined rows! Sum is 3x inflated ($60,000 instead of $20,000).
            cartesian_rows = []
            for item in items:
                for sh in shipments:
                    cartesian_rows.append({"line_id": item["line_id"], "amount": item["amount"], "shipment": sh["shipment_id"]})
            total = sum(r["amount"] for r in cartesian_rows)
            row_count = len(cartesian_rows)
        else:
            # Fixed: Group by line item or calculate item sum distinctly
            total = sum(i["amount"] for i in items)
            row_count = len(items)

        return {
            "scenario": "Scenario B: Duplicate Aggregate Sums",
            "order_id": order_id,
            "mode": mode,
            "reported_total": total,
            "actual_order_total": 20000.0,
            "rows_aggregated": row_count,
            "is_accurate": (total == 20000.0),
            "defect_observed": (total > 20000.0),
            "explanation": "Buggy join created a cartesian fan-out (2 items * 3 shipments = 6 rows), inflating total to $60,000." if mode == "buggy" else "Fixed query aggregates distinct items, producing true total $20,000."
        }

    # SCENARIO C: Invalid Workflow State Transition
    @staticmethod
    def process_invoice_transition(current_status: str, target_status: str, amount: float, credit_approved: bool, mode: str = "buggy") -> Dict[str, Any]:
        """
        Rule: Invoices > $50,000 cannot transition directly from DRAFT to ISSUED.
        They must pass CREDIT_APPROVED first.
        """
        if mode == "buggy":
            # Bug: Direct setter allows any status transition without validating guards
            new_status = target_status
            valid = True
            msg = f"Transitioned directly to {new_status} (Guard bypassed)."
        else:
            # Fixed: Validate state guard
            if amount > 50000.0 and current_status == "DRAFT" and target_status == "ISSUED" and not credit_approved:
                valid = False
                new_status = current_status
                msg = "Validation Error: Invoices exceeding $50,000 require CREDIT_APPROVED status before issuance."
            else:
                valid = True
                new_status = target_status
                msg = f"Valid transition to {new_status}."

        return {
            "scenario": "Scenario C: Invalid Workflow Transition",
            "mode": mode,
            "invoice_amount": amount,
            "current_status": current_status,
            "target_status": target_status,
            "credit_approved": credit_approved,
            "transition_allowed": valid,
            "result_status": new_status,
            "defect_observed": (mode == "buggy" and amount > 50000.0 and not credit_approved and new_status == "ISSUED"),
            "message": msg
        }

    # SCENARIO D: Database Constraint & Transaction Rollback Failure
    @staticmethod
    def execute_batch_settlement(mode: str = "buggy") -> Dict[str, Any]:
        """
        Batch of 3 settlement lines:
        - Line 1: Merchant M-001 ($500) -> Valid
        - Line 2: Merchant M-999 ($1,200) -> Invalid FK (Merchant does not exist in MERCHANT_REGISTRY)
        - Line 3: Merchant M-002 ($300) -> Valid
        """
        # Create an in-memory test db
        mem_conn = sqlite3.connect(":memory:")
        mem_cursor = mem_conn.cursor()
        mem_cursor.execute("PRAGMA foreign_keys = ON;")
        mem_cursor.execute("CREATE TABLE MERCHANTS (merchant_id TEXT PRIMARY KEY, name TEXT);")
        mem_cursor.execute("INSERT INTO MERCHANTS VALUES ('M-001', 'Acme Corp'), ('M-002', 'Global Tech');")
        mem_cursor.execute("""
        CREATE TABLE SETTLEMENT_LINES (
            line_id TEXT PRIMARY KEY,
            merchant_id TEXT NOT NULL REFERENCES MERCHANTS(merchant_id),
            amount REAL NOT NULL
        );
        """)
        mem_conn.commit()

        lines = [
            ("L-1", "M-001", 500.0),
            ("L-2", "M-999", 1200.0),  # Will fail FK constraint!
            ("L-3", "M-002", 300.0)
        ]

        if mode == "buggy":
            # Bug: Autocommit / unhandled exception commits partial lines before failure
            committed_count = 0
            error_captured = None
            for lid, mid, amt in lines:
                try:
                    mem_cursor.execute("INSERT INTO SETTLEMENT_LINES VALUES (?, ?, ?);", (lid, mid, amt))
                    mem_conn.commit() # Flawed per-row commit!
                    committed_count += 1
                except Exception as e:
                    error_captured = f"ORA-02291 / Foreign Key Violation: {str(e)}"
                    break
        else:
            # Fixed: Atomic transaction block with complete rollback on exception
            committed_count = 0
            error_captured = None
            try:
                for lid, mid, amt in lines:
                    mem_cursor.execute("INSERT INTO SETTLEMENT_LINES VALUES (?, ?, ?);", (lid, mid, amt))
                mem_conn.commit()
            except Exception as e:
                mem_conn.rollback() # Proper atomic rollback
                error_captured = f"ORA-02291 / Foreign Key Violation: {str(e)}"

        # Query committed count
        mem_cursor.execute("SELECT COUNT(*) FROM SETTLEMENT_LINES;")
        remaining_lines = mem_cursor.fetchone()[0]
        mem_conn.close()

        return {
            "scenario": "Scenario D: Database Constraint & Rollback Integrity",
            "mode": mode,
            "error_captured": error_captured,
            "committed_lines_count": remaining_lines,
            "is_clean_rollback": (remaining_lines == 0),
            "defect_observed": (mode == "buggy" and remaining_lines > 0),
            "explanation": "Buggy execution committed partial rows (orphaned settlement line L-1 exists in database). Fixed execution rolled back entirely." if mode == "buggy" else "Atomic transaction rolled back completely. Zero orphaned rows remain."
        }

    # SCENARIO E: Regression After Optimization
    @staticmethod
    def calculate_discount(order_amount: float, coupon_code: str, coupon_expiry_date: str, mode: str = "buggy") -> Dict[str, Any]:
        """
        Fixtures:
        - Coupon: "SUMMER20" (20% off)
        - Expiry Date: "2026-06-01"
        - Current Date: "2026-10-29" -> EXPIRED!
        """
        today = "2026-10-29"
        is_expired = (coupon_expiry_date < today)

        if mode == "buggy":
            # Bug: Refactoring optimized percent discount caching but accidentally nested expiration check
            # inside fixed-dollar branch only! Percentage coupons bypass expiration check!
            if coupon_code == "SUMMER20":
                discount = order_amount * 0.20
                final_total = order_amount - discount
                applied = True
            else:
                discount = 0.0
                final_total = order_amount
                applied = False
        else:
            # Fixed: Base validation path checks expiration regardless of coupon type
            if is_expired:
                discount = 0.0
                final_total = order_amount
                applied = False
            elif coupon_code == "SUMMER20":
                discount = order_amount * 0.20
                final_total = order_amount - discount
                applied = True
            else:
                discount = 0.0
                final_total = order_amount
                applied = False

        return {
            "scenario": "Scenario E: Regression After Optimization",
            "mode": mode,
            "order_amount": order_amount,
            "coupon_code": coupon_code,
            "coupon_expiry": coupon_expiry_date,
            "is_expired": is_expired,
            "coupon_applied": applied,
            "discount_amount": discount,
            "final_total": final_total,
            "defect_observed": (mode == "buggy" and applied and is_expired),
            "explanation": "Buggy optimized code accepted expired coupon SUMMER20, leaking $20 on a $100 order!" if mode == "buggy" else "Fixed code successfully rejected expired coupon SUMMER20."
        }

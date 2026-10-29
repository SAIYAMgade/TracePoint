from typing import Dict, Any, List
from ..core.database import db_manager

class ReportRepository:
    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        with db_manager.session() as conn:
            cursor = conn.cursor()

            # 1. Open defects by severity
            cursor.execute("""
            SELECT severity, COUNT(*)
            FROM DEFECTS
            WHERE status NOT IN ('CLOSED', 'REJECTED')
            GROUP BY severity
            """)
            sev_rows = cursor.fetchall()
            sev_map = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for row in sev_rows:
                sev_map[row[0]] = row[1]

            # 2. Defects awaiting reproduction
            cursor.execute("SELECT COUNT(*) FROM DEFECTS WHERE reproduction_status = 'PENDING' AND status NOT IN ('CLOSED', 'REJECTED')")
            awaiting_repro = cursor.fetchone()[0]

            # 3. Investigations without confirmed root causes
            cursor.execute("""
            SELECT COUNT(*) FROM INVESTIGATIONS i
            JOIN DEFECTS d ON i.defect_id = d.defect_id
            WHERE i.confirmed_root_cause IS NULL AND d.status NOT IN ('CLOSED', 'REJECTED')
            """)
            unconfirmed_inv = cursor.fetchone()[0]

            # 4. Fixes awaiting verification
            cursor.execute("""
            SELECT COUNT(*) FROM DEFECTS
            WHERE status IN ('FIX_PROPOSED', 'VALIDATION_REQUIRED')
            """)
            fixes_awaiting = cursor.fetchone()[0]

            # 5. Failed regression tests
            cursor.execute("SELECT COUNT(*) FROM REGRESSION_TESTS WHERE last_outcome = 'FAILED'")
            failed_tests = cursor.fetchone()[0]

            # 6. Releases blocked
            cursor.execute("SELECT COUNT(*) FROM RELEASES WHERE status = 'BLOCKED' OR is_ready = 0")
            blocked_releases = cursor.fetchone()[0]

            # 7. Reopened defects
            cursor.execute("""
            SELECT COUNT(DISTINCT entity_id) FROM AUDIT_LOG
            WHERE entity_type = 'DEFECT' AND action = 'STATUS_TRANSITION'
              AND previous_state LIKE '%CLOSED%' AND new_state LIKE '%OPEN%'
            """)
            reopened = cursor.fetchone()[0]

            # 8. Avg resolution hours
            cursor.execute("""
            SELECT AVG(
                (julianday(resolved_at) - julianday(created_at)) * 24.0
            )
            FROM DEFECTS
            WHERE status = 'CLOSED' AND resolved_at IS NOT NULL
            """)
            avg_res = cursor.fetchone()[0]
            avg_res_rounded = round(avg_res, 1) if avg_res is not None else None

            # Total counts
            cursor.execute("SELECT COUNT(*) FROM DEFECTS WHERE status NOT IN ('CLOSED', 'REJECTED')")
            total_active = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM DEFECTS WHERE status = 'VERIFIED' OR status = 'CLOSED'")
            total_verified = cursor.fetchone()[0]

            return {
                "open_defects_by_severity": sev_map,
                "defects_awaiting_reproduction": awaiting_repro,
                "investigations_without_root_cause": unconfirmed_inv,
                "fixes_awaiting_verification": fixes_awaiting,
                "failed_regression_tests": failed_tests,
                "releases_blocked": blocked_releases,
                "reopened_defects_count": reopened,
                "avg_resolution_hours": avg_res_rounded,
                "total_active_defects": total_active,
                "total_verified_defects": total_verified
            }

    @staticmethod
    def get_report_data(report_name: str) -> Dict[str, Any]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            
            reports = {
                "open_defects_by_severity": {
                    "title": "Open Defects Grouped by Severity",
                    "description": "Aggregates unresolved defects by severity level, highlighting reproduction and verification debt.",
                    "sql": "SELECT * FROM V_OPEN_DEFECTS_BY_SEVERITY"
                },
                "defects_awaiting_verification": {
                    "title": "Defects Awaiting Verification",
                    "description": "Lists defects where a fix has been proposed or validation is actively required.",
                    "sql": "SELECT * FROM V_DEFECTS_AWAITING_VERIFICATION"
                },
                "unconfirmed_investigations": {
                    "title": "Investigations Without Confirmed Root Cause",
                    "description": "Identifies active defect investigations where initial hypotheses have not yet been supported with evidence.",
                    "sql": """
                    SELECT i.investigation_id, i.defect_id, d.title AS defect_title, d.severity,
                           i.problem_statement, i.initial_hypothesis, i.lead_investigator, i.created_at
                    FROM INVESTIGATIONS i
                    JOIN DEFECTS d ON i.defect_id = d.defect_id
                    WHERE i.confirmed_root_cause IS NULL AND d.status NOT IN ('CLOSED', 'REJECTED')
                    """
                },
                "failed_regression_tests": {
                    "title": "Failed Regression Tests by Release",
                    "description": "Correlates failed regression test suites with target releases and affected defects.",
                    "sql": """
                    SELECT rt.test_id, rt.title, rt.test_category, rt.related_defect_id,
                           rt.execution_command, rt.last_outcome, rt.last_run_at
                    FROM REGRESSION_TESTS rt
                    WHERE rt.last_outcome = 'FAILED'
                    """
                },
                "blocked_releases": {
                    "title": "Releases Blocked by Outstanding Checks",
                    "description": "Audits releases that cannot proceed due to failed mandatory checks or open blockers.",
                    "sql": """
                    SELECT r.release_id, r.version_tag, r.status, r.is_ready, r.readiness_score,
                           COUNT(rc.check_id) AS total_checks,
                           SUM(CASE WHEN rc.is_mandatory = 1 AND rc.status = 'FAILED' THEN 1 ELSE 0 END) AS mandatory_failed
                    FROM RELEASES r
                    LEFT JOIN RELEASE_CHECKS rc ON r.release_id = rc.release_id
                    GROUP BY r.release_id, r.version_tag, r.status, r.is_ready, r.readiness_score
                    """
                }
            }

            rep = reports.get(report_name, reports["open_defects_by_severity"])
            cursor.execute(rep["sql"])
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            result_rows = [dict(zip(columns, row)) for row in rows]

            return {
                "report_name": rep["title"],
                "description": rep["description"],
                "sql_source": rep["sql"].strip(),
                "columns": columns,
                "rows": result_rows
            }

from typing import List, Optional, Dict, Any
from ..core.database import db_manager

class TestingRepository:
    @staticmethod
    def get_all_tests() -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT test_id, title, description, test_category, related_defect_id,
                   preconditions, expected_behavior, execution_command,
                   last_outcome, last_run_at, created_at
            FROM REGRESSION_TESTS
            ORDER BY created_at ASC
            """)
            rows = cursor.fetchall()
            cols = [
                "test_id", "title", "description", "test_category", "related_defect_id",
                "preconditions", "expected_behavior", "execution_command",
                "last_outcome", "last_run_at", "created_at"
            ]
            return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    def get_test_by_id(test_id: str) -> Optional[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT test_id, title, description, test_category, related_defect_id,
                   preconditions, expected_behavior, execution_command,
                   last_outcome, last_run_at, created_at
            FROM REGRESSION_TESTS
            WHERE test_id = ?
            """, (test_id,))
            row = cursor.fetchone()
            if not row:
                return None
            cols = [
                "test_id", "title", "description", "test_category", "related_defect_id",
                "preconditions", "expected_behavior", "execution_command",
                "last_outcome", "last_run_at", "created_at"
            ]
            return dict(zip(cols, row))

    @staticmethod
    def update_test_outcome(test_id: str, outcome: str):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE REGRESSION_TESTS
            SET last_outcome = ?, last_run_at = datetime('now')
            WHERE test_id = ?
            """, (outcome, test_id))

    @staticmethod
    def get_test_runs(
        limit: int = 50,
        related_defect_id: Optional[str] = None,
        related_release_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []
            if related_defect_id:
                conditions.append("related_defect_id = ?")
                params.append(related_defect_id)
            if related_release_id:
                conditions.append("related_release_id = ?")
                params.append(related_release_id)

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"""
            SELECT run_id, test_suite_id, execution_method, command, outcome,
                   passed_count, failed_count, skipped_count, duration_ms,
                   output_summary, environment_meta, related_defect_id,
                   related_release_id, triggered_by, started_at, completed_at
            FROM TEST_RUNS
            {where_clause}
            ORDER BY completed_at DESC
            LIMIT ?
            """
            cursor.execute(sql, params + [limit])
            rows = cursor.fetchall()
            cols = [
                "run_id", "test_suite_id", "execution_method", "command", "outcome",
                "passed_count", "failed_count", "skipped_count", "duration_ms",
                "output_summary", "environment_meta", "related_defect_id",
                "related_release_id", "triggered_by", "started_at", "completed_at"
            ]
            return [dict(zip(cols, row)) for row in rows]

    @staticmethod
    def record_run(data: Dict[str, Any]) -> Dict[str, Any]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO TEST_RUNS (
                run_id, test_suite_id, execution_method, command, outcome,
                passed_count, failed_count, skipped_count, duration_ms,
                output_summary, environment_meta, related_defect_id,
                related_release_id, triggered_by, started_at, completed_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["run_id"], data["test_suite_id"], data["execution_method"],
                data["command"], data["outcome"], data.get("passed_count", 0),
                data.get("failed_count", 0), data.get("skipped_count", 0),
                data.get("duration_ms", 0), data.get("output_summary"),
                data.get("environment_meta"), data.get("related_defect_id"),
                data.get("related_release_id"), data["triggered_by"],
                data["started_at"], data["completed_at"]
            ))
            return data

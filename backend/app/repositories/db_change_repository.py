from typing import List, Optional, Dict, Any
from ..core.database import db_manager

class DBChangeRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT change_id, change_name, change_type, target_schema,
                   sql_script, rollback_script, pre_check_query, post_check_query,
                   status, execution_log, applied_at, applied_by, oracle_object_name
            FROM DATABASE_CHANGES
            ORDER BY change_id ASC
            """)
            rows = cursor.fetchall()
            cols = [
                "change_id", "change_name", "change_type", "target_schema",
                "sql_script", "rollback_script", "pre_check_query", "post_check_query",
                "status", "execution_log", "applied_at", "applied_by", "oracle_object_name"
            ]
            return [dict(zip(cols, r)) for r in rows]

    @staticmethod
    def get_by_id(change_id: str) -> Optional[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT change_id, change_name, change_type, target_schema,
                   sql_script, rollback_script, pre_check_query, post_check_query,
                   status, execution_log, applied_at, applied_by, oracle_object_name
            FROM DATABASE_CHANGES
            WHERE change_id = ?
            """, (change_id,))
            row = cursor.fetchone()
            if not row:
                return None
            cols = [
                "change_id", "change_name", "change_type", "target_schema",
                "sql_script", "rollback_script", "pre_check_query", "post_check_query",
                "status", "execution_log", "applied_at", "applied_by", "oracle_object_name"
            ]
            return dict(zip(cols, row))

    @staticmethod
    def update_status(
        change_id: str,
        status: str,
        execution_log: str,
        applied_by: Optional[str] = None
    ):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            if status == "APPLIED":
                cursor.execute("""
                UPDATE DATABASE_CHANGES
                SET status = ?, execution_log = ?, applied_at = datetime('now'), applied_by = ?
                WHERE change_id = ?
                """, (status, execution_log, applied_by, change_id))
            else:
                cursor.execute("""
                UPDATE DATABASE_CHANGES
                SET status = ?, execution_log = ?
                WHERE change_id = ?
                """, (status, execution_log, change_id))

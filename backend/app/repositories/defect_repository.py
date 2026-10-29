from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from ..core.database import db_manager
from ..core.logging import logger

class DefectRepository:
    @staticmethod
    def get_all(
        skip: int = 0,
        limit: int = 50,
        severity: Optional[str] = None,
        status: Optional[str] = None,
        component: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []

            if severity:
                conditions.append("severity = ?")
                params.append(severity.upper())
            if status:
                conditions.append("status = ?")
                params.append(status.upper())
            if component:
                conditions.append("affected_component = ?")
                params.append(component)
            if search:
                conditions.append("(title LIKE ? OR description LIKE ? OR defect_id LIKE ?)")
                search_term = f"%{search}%"
                params.extend([search_term, search_term, search_term])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            # Count total
            count_sql = f"SELECT COUNT(*) FROM DEFECTS{where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()[0]

            # Fetch rows
            query_sql = f"""
            SELECT defect_id, title, description, severity, priority,
                   affected_component, environment, status, reproduction_status,
                   expected_behavior, actual_behavior, root_cause_explanation,
                   proposed_correction, verification_status, assigned_owner,
                   associated_regression_test_id, associated_release_id,
                   created_at, updated_at, resolved_at
            FROM DEFECTS
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """
            cursor.execute(query_sql, params + [limit, skip])
            rows = cursor.fetchall()

            columns = [
                "defect_id", "title", "description", "severity", "priority",
                "affected_component", "environment", "status", "reproduction_status",
                "expected_behavior", "actual_behavior", "root_cause_explanation",
                "proposed_correction", "verification_status", "assigned_owner",
                "associated_regression_test_id", "associated_release_id",
                "created_at", "updated_at", "resolved_at"
            ]
            items = [dict(zip(columns, row)) for row in rows]
            return items, total

    @staticmethod
    def get_by_id(defect_id: str) -> Optional[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT defect_id, title, description, severity, priority,
                   affected_component, environment, status, reproduction_status,
                   expected_behavior, actual_behavior, root_cause_explanation,
                   proposed_correction, verification_status, assigned_owner,
                   associated_regression_test_id, associated_release_id,
                   created_at, updated_at, resolved_at
            FROM DEFECTS
            WHERE defect_id = ?
            """, (defect_id,))
            row = cursor.fetchone()
            if not row:
                return None
            columns = [
                "defect_id", "title", "description", "severity", "priority",
                "affected_component", "environment", "status", "reproduction_status",
                "expected_behavior", "actual_behavior", "root_cause_explanation",
                "proposed_correction", "verification_status", "assigned_owner",
                "associated_regression_test_id", "associated_release_id",
                "created_at", "updated_at", "resolved_at"
            ]
            return dict(zip(columns, row))

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO DEFECTS (
                defect_id, title, description, severity, priority,
                affected_component, environment, status, reproduction_status,
                expected_behavior, actual_behavior, root_cause_explanation,
                proposed_correction, verification_status, assigned_owner,
                associated_regression_test_id, associated_release_id,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                data["defect_id"], data["title"], data["description"], data["severity"],
                data["priority"], data["affected_component"], data["environment"],
                data.get("status", "OPEN"), data.get("reproduction_status", "PENDING"),
                data.get("expected_behavior"), data.get("actual_behavior"),
                data.get("root_cause_explanation"), data.get("proposed_correction"),
                data.get("verification_status", "UNVERIFIED"), data["assigned_owner"],
                data.get("associated_regression_test_id"), data.get("associated_release_id")
            ))
        return DefectRepository.get_by_id(data["defect_id"])

    @staticmethod
    def update(defect_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            set_clauses = []
            params = []
            for k, v in updates.items():
                if v is not None:
                    set_clauses.append(f"{k} = ?")
                    params.append(v)
            if set_clauses:
                set_clauses.append("updated_at = datetime('now')")
                sql = f"UPDATE DEFECTS SET {', '.join(set_clauses)} WHERE defect_id = ?"
                params.append(defect_id)
                cursor.execute(sql, params)
        return DefectRepository.get_by_id(defect_id)

    @staticmethod
    def update_status(defect_id: str, new_status: str, resolved_at: Optional[str] = None):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            if resolved_at:
                cursor.execute("""
                UPDATE DEFECTS
                SET status = ?, updated_at = datetime('now'), resolved_at = ?
                WHERE defect_id = ?
                """, (new_status, resolved_at, defect_id))
            else:
                cursor.execute("""
                UPDATE DEFECTS
                SET status = ?, updated_at = datetime('now')
                WHERE defect_id = ?
                """, (new_status, defect_id))

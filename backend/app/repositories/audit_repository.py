from typing import List, Optional, Dict, Any
import uuid
from ..core.database import db_manager

class AuditRepository:
    @staticmethod
    def record(
        entity_type: str,
        entity_id: str,
        action: str,
        actor: str,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        audit_id = f"AUD-{uuid.uuid4().hex[:10].upper()}"
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO AUDIT_LOG (
                audit_id, entity_type, entity_id, action,
                previous_state, new_state, actor, correlation_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                audit_id, entity_type, entity_id, action,
                previous_state, new_state, actor, correlation_id
            ))
            return {
                "audit_id": audit_id,
                "entity_type": entity_type,
                "entity_id": entity_id,
                "action": action,
                "previous_state": previous_state,
                "new_state": new_state,
                "actor": actor,
                "correlation_id": correlation_id
            }

    @staticmethod
    def get_logs(
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            conditions = []
            params = []
            if entity_type:
                conditions.append("entity_type = ?")
                params.append(entity_type.upper())
            if entity_id:
                conditions.append("entity_id = ?")
                params.append(entity_id)

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            sql = f"""
            SELECT audit_id, entity_type, entity_id, action,
                   previous_state, new_state, actor, correlation_id, created_at
            FROM AUDIT_LOG
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
            """
            cursor.execute(sql, params + [limit])
            rows = cursor.fetchall()
            cols = [
                "audit_id", "entity_type", "entity_id", "action",
                "previous_state", "new_state", "actor", "correlation_id", "created_at"
            ]
            return [dict(zip(cols, r)) for r in rows]

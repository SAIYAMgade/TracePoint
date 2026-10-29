from typing import List, Optional, Dict, Any
from ..core.database import db_manager

class EvidenceRepository:
    @staticmethod
    def get_by_defect(defect_id: str) -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT evidence_id, defect_id, investigation_id, evidence_type,
                   title, error_code, sanitized_payload, component,
                   environment, correlation_id, collected_by, created_at
            FROM EVIDENCE
            WHERE defect_id = ?
            ORDER BY created_at DESC
            """, (defect_id,))
            rows = cursor.fetchall()
            columns = [
                "evidence_id", "defect_id", "investigation_id", "evidence_type",
                "title", "error_code", "sanitized_payload", "component",
                "environment", "correlation_id", "collected_by", "created_at"
            ]
            return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO EVIDENCE (
                evidence_id, defect_id, investigation_id, evidence_type,
                title, error_code, sanitized_payload, component,
                environment, correlation_id, collected_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                data["evidence_id"], data["defect_id"], data.get("investigation_id"),
                data["evidence_type"], data["title"], data.get("error_code"),
                data["sanitized_payload"], data.get("component"), data.get("environment"),
                data.get("correlation_id"), data["collected_by"]
            ))
            return data

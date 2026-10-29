from typing import List, Optional, Dict, Any
import json
from ..core.database import db_manager
from ..core.logging import logger

class InvestigationRepository:
    @staticmethod
    def get_by_defect_id(defect_id: str) -> Optional[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT investigation_id, defect_id, problem_statement, observed_symptoms,
                   initial_hypothesis, candidate_causes, confirmed_root_cause,
                   proposed_correction, regression_risk, verification_plan,
                   final_conclusion, status, lead_investigator, created_at, updated_at
            FROM INVESTIGATIONS
            WHERE defect_id = ?
            """, (defect_id,))
            row = cursor.fetchone()
            if not row:
                return None
            columns = [
                "investigation_id", "defect_id", "problem_statement", "observed_symptoms",
                "initial_hypothesis", "candidate_causes", "confirmed_root_cause",
                "proposed_correction", "regression_risk", "verification_plan",
                "final_conclusion", "status", "lead_investigator", "created_at", "updated_at"
            ]
            data = dict(zip(columns, row))
            data["events"] = InvestigationRepository.get_events(data["investigation_id"])
            return data

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO INVESTIGATIONS (
                investigation_id, defect_id, problem_statement, observed_symptoms,
                initial_hypothesis, candidate_causes, confirmed_root_cause,
                proposed_correction, regression_risk, verification_plan,
                final_conclusion, status, lead_investigator, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """, (
                data["investigation_id"], data["defect_id"], data["problem_statement"],
                data["observed_symptoms"], data["initial_hypothesis"],
                data.get("candidate_causes"), data.get("confirmed_root_cause"),
                data.get("proposed_correction"), data.get("regression_risk"),
                data.get("verification_plan"), data.get("final_conclusion"),
                data.get("status", "IN_PROGRESS"), data["lead_investigator"]
            ))
        return InvestigationRepository.get_by_defect_id(data["defect_id"])

    @staticmethod
    def update(investigation_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            set_clauses = []
            params = []
            for k, v in updates.items():
                if v is not None and k != "events":
                    set_clauses.append(f"{k} = ?")
                    params.append(v)
            if set_clauses:
                set_clauses.append("updated_at = datetime('now')")
                sql = f"UPDATE INVESTIGATIONS SET {', '.join(set_clauses)} WHERE investigation_id = ?"
                params.append(investigation_id)
                cursor.execute(sql, params)

            cursor.execute("SELECT defect_id FROM INVESTIGATIONS WHERE investigation_id = ?", (investigation_id,))
            row = cursor.fetchone()
            defect_id = row[0] if row else None
        return InvestigationRepository.get_by_defect_id(defect_id) if defect_id else None

    @staticmethod
    def get_events(investigation_id: str) -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT event_id, investigation_id, event_type, title, details, actor, created_at
            FROM INVESTIGATION_EVENTS
            WHERE investigation_id = ?
            ORDER BY created_at ASC
            """, (investigation_id,))
            rows = cursor.fetchall()
            columns = ["event_id", "investigation_id", "event_type", "title", "details", "actor", "created_at"]
            return [dict(zip(columns, row)) for row in rows]

    @staticmethod
    def add_event(data: Dict[str, Any]) -> Dict[str, Any]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO INVESTIGATION_EVENTS (
                event_id, investigation_id, event_type, title, details, actor, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                data["event_id"], data["investigation_id"], data["event_type"],
                data["title"], data.get("details"), data["actor"]
            ))
            return data

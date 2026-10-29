from typing import List, Optional, Dict, Any
import json
from ..core.database import db_manager

class ReproductionRepository:
    @staticmethod
    def get_by_defect(defect_id: str) -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT reproduction_id, defect_id, preconditions, environment_info,
                   app_version, steps_json, synthetic_fixture_ref,
                   expected_result, actual_result, error_message,
                   frequency, outcome, notes, executed_by, created_at
            FROM REPRODUCTIONS
            WHERE defect_id = ?
            ORDER BY created_at DESC
            """, (defect_id,))
            rows = cursor.fetchall()
            items = []
            for r in rows:
                steps = json.loads(r[5]) if r[5] else []
                items.append({
                    "reproduction_id": r[0],
                    "defect_id": r[1],
                    "preconditions": r[2],
                    "environment_info": r[3],
                    "app_version": r[4],
                    "steps": steps,
                    "synthetic_fixture_ref": r[6],
                    "expected_result": r[7],
                    "actual_result": r[8],
                    "error_message": r[9],
                    "frequency": r[10],
                    "outcome": r[11],
                    "notes": r[12],
                    "executed_by": r[13],
                    "created_at": r[14]
                })
            return items

    @staticmethod
    def create(data: Dict[str, Any]) -> Dict[str, Any]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            steps_json = json.dumps(data["steps"]) if isinstance(data["steps"], list) else data["steps"]
            cursor.execute("""
            INSERT INTO REPRODUCTIONS (
                reproduction_id, defect_id, preconditions, environment_info,
                app_version, steps_json, synthetic_fixture_ref,
                expected_result, actual_result, error_message,
                frequency, outcome, notes, executed_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                data["reproduction_id"], data["defect_id"], data.get("preconditions"),
                data.get("environment_info"), data.get("app_version"),
                steps_json, data.get("synthetic_fixture_ref"),
                data.get("expected_result"), data.get("actual_result"),
                data.get("error_message"), data.get("frequency", "ALWAYS"),
                data["outcome"], data.get("notes"), data["executed_by"]
            ))
            # Also update reproduction_status on DEFECTS
            cursor.execute("""
            UPDATE DEFECTS
            SET reproduction_status = ?, updated_at = datetime('now')
            WHERE defect_id = ?
            """, (data["outcome"], data["defect_id"]))

            return data

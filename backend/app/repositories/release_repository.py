from typing import List, Optional, Dict, Any
from ..core.database import db_manager

class ReleaseRepository:
    @staticmethod
    def get_all() -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT release_id, version_tag, summary, status, rollback_plan,
                   is_ready, readiness_score, created_at, updated_at, released_at
            FROM RELEASES
            ORDER BY created_at DESC
            """)
            rows = cursor.fetchall()
            cols = [
                "release_id", "version_tag", "summary", "status", "rollback_plan",
                "is_ready", "readiness_score", "created_at", "updated_at", "released_at"
            ]
            releases = []
            for r in rows:
                item = dict(zip(cols, r))
                item["is_ready"] = bool(item["is_ready"])
                item["checks"] = ReleaseRepository.get_checks(item["release_id"])
                releases.append(item)
            return releases

    @staticmethod
    def get_by_id(release_id: str) -> Optional[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT release_id, version_tag, summary, status, rollback_plan,
                   is_ready, readiness_score, created_at, updated_at, released_at
            FROM RELEASES
            WHERE release_id = ?
            """, (release_id,))
            row = cursor.fetchone()
            if not row:
                return None
            cols = [
                "release_id", "version_tag", "summary", "status", "rollback_plan",
                "is_ready", "readiness_score", "created_at", "updated_at", "released_at"
            ]
            data = dict(zip(cols, row))
            data["is_ready"] = bool(data["is_ready"])
            data["checks"] = ReleaseRepository.get_checks(release_id)
            return data

    @staticmethod
    def get_checks(release_id: str) -> List[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT check_id, release_id, check_name, check_category, is_mandatory,
                   status, waiver_reason, verified_at, verified_by, evidence_details
            FROM RELEASE_CHECKS
            WHERE release_id = ?
            ORDER BY is_mandatory DESC, check_name ASC
            """, (release_id,))
            rows = cursor.fetchall()
            cols = [
                "check_id", "release_id", "check_name", "check_category", "is_mandatory",
                "status", "waiver_reason", "verified_at", "verified_by", "evidence_details"
            ]
            items = []
            for r in rows:
                chk = dict(zip(cols, r))
                chk["is_mandatory"] = bool(chk["is_mandatory"])
                items.append(chk)
            return items

    @staticmethod
    def update_check(check_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE RELEASE_CHECKS
            SET status = ?, waiver_reason = ?, verified_at = datetime('now'),
                verified_by = ?, evidence_details = ?
            WHERE check_id = ?
            """, (
                updates["status"], updates.get("waiver_reason"),
                updates["verified_by"], updates.get("evidence_details"),
                check_id
            ))
            cursor.execute("""
            SELECT check_id, release_id, check_name, check_category, is_mandatory,
                   status, waiver_reason, verified_at, verified_by, evidence_details
            FROM RELEASE_CHECKS
            WHERE check_id = ?
            """, (check_id,))
            row = cursor.fetchone()
            if not row:
                return None
            cols = [
                "check_id", "release_id", "check_name", "check_category", "is_mandatory",
                "status", "waiver_reason", "verified_at", "verified_by", "evidence_details"
            ]
            res = dict(zip(cols, row))
            res["is_mandatory"] = bool(res["is_mandatory"])
            return res

    @staticmethod
    def update_readiness(release_id: str, is_ready: bool, score: float, status: str):
        with db_manager.session() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE RELEASES
            SET is_ready = ?, readiness_score = ?, status = ?, updated_at = datetime('now')
            WHERE release_id = ?
            """, (1 if is_ready else 0, score, status, release_id))

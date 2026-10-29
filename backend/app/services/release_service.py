from typing import Dict, Any, List
from fastapi import HTTPException
from ..repositories.release_repository import ReleaseRepository
from ..repositories.defect_repository import DefectRepository
from ..repositories.testing_repository import TestingRepository
from ..repositories.audit_repository import AuditRepository
from ..core.database import db_manager
from ..core.logging import logger

class ReleaseService:
    @staticmethod
    def evaluate_readiness(release_id: str) -> Dict[str, Any]:
        release = ReleaseRepository.get_by_id(release_id)
        if not release:
            raise HTTPException(status_code=404, detail=f"Release {release_id} not found")

        if db_manager.is_oracle:
            return ReleaseService._evaluate_oracle(release_id)
        else:
            return ReleaseService._evaluate_local(release)

    @staticmethod
    def _evaluate_oracle(release_id: str) -> Dict[str, Any]:
        try:
            with db_manager.session() as conn:
                cursor = conn.cursor()
                is_ready = cursor.var(int)
                score = cursor.var(float)
                blockers = cursor.var(str)
                cursor.callproc(
                    "PKG_RELEASE_GATE.evaluate_readiness",
                    [release_id, is_ready, score, blockers]
                )
                ready_val = bool(is_ready.getvalue())
                score_val = score.getvalue()
                blockers_val = blockers.getvalue()
                rel = ReleaseRepository.get_by_id(release_id)
                return {
                    "release_id": release_id,
                    "is_ready": ready_val,
                    "readiness_score": score_val,
                    "status": rel["status"],
                    "blocking_reasons": [blockers_val] if blockers_val else [],
                    "evaluated_at": rel["updated_at"]
                }
        except Exception as e:
            logger.error("Oracle PL/SQL Release Gate evaluation failed: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Database execution error: {str(e)}")

    @staticmethod
    def _evaluate_local(release: Dict[str, Any]) -> Dict[str, Any]:
        release_id = release["release_id"]
        checks = ReleaseRepository.get_checks(release_id)
        blocking_reasons: List[str] = []

        total_checks = len(checks)
        passed_or_waived = 0

        # 1. Evaluate release checks
        for chk in checks:
            if chk["status"] in ["PASSED", "WAIVED"]:
                passed_or_waived += 1
            elif chk["is_mandatory"]:
                if chk["status"] == "FAILED":
                    blocking_reasons.append(f"Mandatory release check FAILED: {chk['check_name']}")
                elif chk["status"] == "PENDING":
                    blocking_reasons.append(f"Mandatory release check PENDING: {chk['check_name']}")

        # 2. Check for open Critical/High defects linked to release
        defects, _ = DefectRepository.get_all(limit=100)
        open_blockers = [
            d for d in defects
            if d.get("associated_release_id") == release_id
            and d["severity"] in ["CRITICAL", "HIGH"]
            and d["status"] not in ["CLOSED", "VERIFIED"]
        ]
        if open_blockers:
            blocking_reasons.append(
                f"{len(open_blockers)} open Critical/High defect(s) unresolved: {', '.join(d['defect_id'] for d in open_blockers)}"
            )

        # 3. Check for failed test runs linked to this release
        runs = TestingRepository.get_test_runs(related_release_id=release_id, limit=20)
        failed_runs = [r for r in runs if r["outcome"] == "FAILED"]
        if failed_runs:
            blocking_reasons.append(f"{len(failed_runs)} failed automated test run(s) recorded against this release")

        # Calculate readiness score
        score = round((passed_or_waived / total_checks * 100), 1) if total_checks > 0 else 0.0

        is_ready = (len(blocking_reasons) == 0 and total_checks > 0)
        new_status = "READY_FOR_REVIEW" if is_ready else "BLOCKED"

        # Update database record
        ReleaseRepository.update_readiness(release_id, is_ready, score, new_status)

        # Audit
        AuditRepository.record(
            entity_type="RELEASE",
            entity_id=release_id,
            action="READINESS_EVALUATION",
            actor="SYSTEM_GATE_ENGINE",
            new_state=f"Score: {score}%, Ready: {is_ready}, Blockers: {len(blocking_reasons)}",
            correlation_id=f"GATE-{release_id}"
        )

        rel = ReleaseRepository.get_by_id(release_id)
        return {
            "release_id": release_id,
            "is_ready": is_ready,
            "readiness_score": score,
            "status": new_status,
            "blocking_reasons": blocking_reasons,
            "evaluated_at": rel["updated_at"]
        }

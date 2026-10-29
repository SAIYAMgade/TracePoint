from typing import Dict, Any, Optional
from datetime import datetime
from fastapi import HTTPException
from ..repositories.defect_repository import DefectRepository
from ..repositories.evidence_repository import EvidenceRepository
from ..repositories.audit_repository import AuditRepository
from ..core.database import db_manager
from ..core.logging import logger

ALLOWED_TRANSITIONS = {
    'OPEN': ['REPRODUCED', 'INVESTIGATING', 'REJECTED', 'DUPLICATE', 'INCONCLUSIVE'],
    'REPRODUCED': ['INVESTIGATING', 'FIX_PROPOSED', 'INCONCLUSIVE'],
    'INVESTIGATING': ['FIX_PROPOSED', 'INCONCLUSIVE', 'REJECTED', 'REPRODUCED'],
    'FIX_PROPOSED': ['VALIDATION_REQUIRED', 'INVESTIGATING'],
    'VALIDATION_REQUIRED': ['VERIFIED', 'FIX_PROPOSED', 'INVESTIGATING'],
    'VERIFIED': ['CLOSED', 'OPEN'],
    'INCONCLUSIVE': ['INVESTIGATING', 'CLOSED', 'OPEN'],
    'CLOSED': ['OPEN'],
    'REJECTED': ['OPEN'],
    'DUPLICATE': ['OPEN'],
}

class DefectService:
    @staticmethod
    def transition_defect(defect_id: str, target_status: str, actor: str, reason: str) -> Dict[str, Any]:
        defect = DefectRepository.get_by_id(defect_id)
        if not defect:
            raise HTTPException(status_code=404, detail=f"Defect {defect_id} not found")

        current_status = defect["status"]
        if current_status == target_status:
            return defect

        # Check if connected to Oracle Database
        if db_manager.is_oracle:
            return DefectService._transition_oracle(defect_id, current_status, target_status, actor, reason)
        else:
            return DefectService._transition_local(defect, target_status, actor, reason)

    @staticmethod
    def _transition_oracle(defect_id: str, current_status: str, target_status: str, actor: str, reason: str) -> Dict[str, Any]:
        try:
            with db_manager.session() as conn:
                cursor = conn.cursor()
                status_code = cursor.var(int)
                message = cursor.var(str)
                cursor.callproc(
                    "PKG_DEFECT_LIFECYCLE.transition_defect",
                    [defect_id, target_status, actor, reason, status_code, message]
                )
                code = status_code.getvalue()
                msg = message.getvalue()
                if code != 0:
                    raise HTTPException(status_code=422, detail=f"Oracle PL/SQL Transition Rejected: {msg}")
                return DefectRepository.get_by_id(defect_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error("PL/SQL execution failed: %s", str(e))
            raise HTTPException(status_code=500, detail=f"Database execution error: {str(e)}")

    @staticmethod
    def _transition_local(defect: Dict[str, Any], target_status: str, actor: str, reason: str) -> Dict[str, Any]:
        current_status = defect["status"]
        allowed = ALLOWED_TRANSITIONS.get(current_status, [])
        if target_status not in allowed:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid state transition: Cannot transition defect from '{current_status}' to '{target_status}'. Allowed transitions: {allowed}"
            )

        # Integrity guard: Cannot transition to VERIFIED without completed test verification
        if target_status == "VERIFIED":
            evidence_items = EvidenceRepository.get_by_defect(defect["defect_id"])
            if defect["verification_status"] != "VERIFIED" and len(evidence_items) == 0:
                raise HTTPException(
                    status_code=422,
                    detail="Cannot transition defect to VERIFIED: Verification status must be VERIFIED and supporting technical evidence must be attached."
                )

        # Update defect status
        resolved_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S") if target_status in ["VERIFIED", "CLOSED"] else None
        DefectRepository.update_status(defect["defect_id"], target_status, resolved_at)

        # Record immutable audit log
        AuditRepository.record(
            entity_type="DEFECT",
            entity_id=defect["defect_id"],
            action="STATUS_TRANSITION",
            actor=actor,
            previous_state=current_status,
            new_state=f"{target_status} [Reason: {reason}]",
            correlation_id=f"TXN-{defect['defect_id']}"
        )

        return DefectRepository.get_by_id(defect["defect_id"])

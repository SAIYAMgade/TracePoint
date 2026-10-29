from fastapi import APIRouter, Query
from typing import Optional, List

from ..schemas.audit import AuditLogResponse
from ..repositories.audit_repository import AuditRepository

router = APIRouter(prefix="/audit", tags=["Audit Log"])

@router.get("", response_model=List[AuditLogResponse])
def get_audit_trail(
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    limit: int = Query(100, ge=1, le=500)
):
    return AuditRepository.get_logs(entity_type=entity_type, entity_id=entity_id, limit=limit)

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import uuid

from ..schemas.defects import (
    DefectCreate, DefectUpdate, DefectTransitionRequest,
    DefectResponse, DefectListResponse
)
from ..schemas.reproductions import ReproductionCreate, ReproductionResponse
from ..schemas.evidence import EvidenceCreate, EvidenceResponse
from ..repositories.defect_repository import DefectRepository
from ..repositories.reproduction_repository import ReproductionRepository
from ..repositories.evidence_repository import EvidenceRepository
from ..repositories.audit_repository import AuditRepository
from ..services.defect_service import DefectService

router = APIRouter(prefix="/defects", tags=["Defects"])

@router.get("", response_model=DefectListResponse)
def list_defects(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    severity: Optional[str] = None,
    status: Optional[str] = None,
    component: Optional[str] = None,
    search: Optional[str] = None
):
    items, total = DefectRepository.get_all(
        skip=skip, limit=limit, severity=severity,
        status=status, component=component, search=search
    )
    return {
        "items": items,
        "total": total,
        "page": (skip // limit) + 1,
        "page_size": limit
    }

@router.get("/{defect_id}", response_model=DefectResponse)
def get_defect(defect_id: str):
    defect = DefectRepository.get_by_id(defect_id)
    if not defect:
        raise HTTPException(status_code=404, detail=f"Defect {defect_id} not found")
    return defect

@router.post("", response_model=DefectResponse, status_code=201)
def create_defect(payload: DefectCreate):
    defect_id = f"DEF-{uuid.uuid4().hex[:6].upper()}"
    data = payload.model_dump()
    data["defect_id"] = defect_id
    data["status"] = "OPEN"
    data["reproduction_status"] = "PENDING"
    data["verification_status"] = "UNVERIFIED"

    created = DefectRepository.create(data)

    AuditRepository.record(
        entity_type="DEFECT",
        entity_id=defect_id,
        action="CREATED",
        actor=payload.assigned_owner,
        new_state=f"Status: OPEN, Severity: {payload.severity}",
        correlation_id=f"TXN-{defect_id}"
    )

    return created

@router.put("/{defect_id}", response_model=DefectResponse)
def update_defect(defect_id: str, payload: DefectUpdate):
    defect = DefectRepository.get_by_id(defect_id)
    if not defect:
        raise HTTPException(status_code=404, detail=f"Defect {defect_id} not found")

    updated = DefectRepository.update(defect_id, payload.model_dump(exclude_unset=True))
    return updated

@router.post("/{defect_id}/transition", response_model=DefectResponse)
def transition_defect_status(defect_id: str, payload: DefectTransitionRequest):
    return DefectService.transition_defect(
        defect_id=defect_id,
        target_status=payload.target_status.value,
        actor=payload.actor,
        reason=payload.reason
    )

# Reproductions Sub-resource
@router.get("/{defect_id}/reproductions", response_model=List[ReproductionResponse])
def get_defect_reproductions(defect_id: str):
    return ReproductionRepository.get_by_defect(defect_id)

@router.post("/{defect_id}/reproductions", response_model=ReproductionResponse, status_code=201)
def add_defect_reproduction(defect_id: str, payload: ReproductionCreate):
    defect = DefectRepository.get_by_id(defect_id)
    if not defect:
        raise HTTPException(status_code=404, detail=f"Defect {defect_id} not found")

    repro_id = f"REP-{uuid.uuid4().hex[:6].upper()}"
    data = payload.model_dump()
    data["reproduction_id"] = repro_id
    data["defect_id"] = defect_id

    created = ReproductionRepository.create(data)

    AuditRepository.record(
        entity_type="DEFECT",
        entity_id=defect_id,
        action="REPRODUCTION_RECORDED",
        actor=payload.executed_by,
        new_state=f"Outcome: {payload.outcome}",
        correlation_id=f"REPRO-{repro_id}"
    )

    return created

# Evidence Sub-resource
@router.get("/{defect_id}/evidence", response_model=List[EvidenceResponse])
def get_defect_evidence(defect_id: str):
    return EvidenceRepository.get_by_defect(defect_id)

@router.post("/{defect_id}/evidence", response_model=EvidenceResponse, status_code=201)
def add_defect_evidence(defect_id: str, payload: EvidenceCreate):
    defect = DefectRepository.get_by_id(defect_id)
    if not defect:
        raise HTTPException(status_code=404, detail=f"Defect {defect_id} not found")

    evi_id = f"EVI-{uuid.uuid4().hex[:6].upper()}"
    data = payload.model_dump()
    data["evidence_id"] = evi_id
    data["defect_id"] = defect_id

    created = EvidenceRepository.create(data)

    AuditRepository.record(
        entity_type="EVIDENCE",
        entity_id=evi_id,
        action="ATTACHED",
        actor=payload.collected_by,
        new_state=f"Type: {payload.evidence_type}, Defect: {defect_id}",
        correlation_id=f"EVI-{evi_id}"
    )

    return created

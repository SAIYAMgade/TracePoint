from fastapi import APIRouter, HTTPException
from typing import Optional, List
import uuid

from ..schemas.investigations import (
    InvestigationCreate, InvestigationUpdate, InvestigationResponse,
    InvestigationEventCreate, InvestigationEventResponse
)
from ..repositories.investigation_repository import InvestigationRepository
from ..repositories.defect_repository import DefectRepository
from ..repositories.audit_repository import AuditRepository

router = APIRouter(prefix="/investigations", tags=["Investigations"])

@router.get("/defect/{defect_id}", response_model=InvestigationResponse)
def get_investigation_by_defect(defect_id: str):
    inv = InvestigationRepository.get_by_defect_id(defect_id)
    if not inv:
        raise HTTPException(status_code=404, detail=f"No investigation found for defect {defect_id}")
    return inv

@router.post("", response_model=InvestigationResponse, status_code=201)
def create_investigation(payload: InvestigationCreate):
    defect = DefectRepository.get_by_id(payload.defect_id)
    if not defect:
        raise HTTPException(status_code=404, detail=f"Defect {payload.defect_id} not found")

    existing = InvestigationRepository.get_by_defect_id(payload.defect_id)
    if existing:
        raise HTTPException(status_code=400, detail=f"Investigation already exists for defect {payload.defect_id}")

    inv_id = f"INV-{uuid.uuid4().hex[:6].upper()}"
    data = payload.model_dump()
    data["investigation_id"] = inv_id

    created = InvestigationRepository.create(data)

    # Initial event
    evt_id = f"EVT-{uuid.uuid4().hex[:6].upper()}"
    InvestigationRepository.add_event({
        "event_id": evt_id,
        "investigation_id": inv_id,
        "event_type": "INVESTIGATION_STARTED",
        "title": "Investigation initialized",
        "details": f"Lead investigator: {payload.lead_investigator}. Hypothesis: {payload.initial_hypothesis[:100]}",
        "actor": payload.lead_investigator
    })

    AuditRepository.record(
        entity_type="INVESTIGATION",
        entity_id=inv_id,
        action="STARTED",
        actor=payload.lead_investigator,
        new_state=f"Defect: {payload.defect_id}",
        correlation_id=f"INV-{inv_id}"
    )

    return InvestigationRepository.get_by_defect_id(payload.defect_id)

@router.put("/{investigation_id}", response_model=InvestigationResponse)
def update_investigation(investigation_id: str, payload: InvestigationUpdate):
    updated = InvestigationRepository.update(investigation_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail=f"Investigation {investigation_id} not found")

    # If confirmed_root_cause is updated, log an event
    if payload.confirmed_root_cause:
        evt_id = f"EVT-{uuid.uuid4().hex[:6].upper()}"
        InvestigationRepository.add_event({
            "event_id": evt_id,
            "investigation_id": investigation_id,
            "event_type": "ROOT_CAUSE_CONFIRMED",
            "title": "Root cause confirmed with technical evidence",
            "details": payload.confirmed_root_cause[:300],
            "actor": payload.lead_investigator or "lead.investigator"
        })

    return updated

@router.post("/{investigation_id}/events", response_model=InvestigationEventResponse, status_code=201)
def add_investigation_event(investigation_id: str, payload: InvestigationEventCreate):
    evt_id = f"EVT-{uuid.uuid4().hex[:6].upper()}"
    data = payload.model_dump()
    data["event_id"] = evt_id
    data["investigation_id"] = investigation_id

    added = InvestigationRepository.add_event(data)
    added["created_at"] = "just now"
    return added

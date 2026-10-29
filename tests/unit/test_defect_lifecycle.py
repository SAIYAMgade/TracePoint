import pytest
import uuid
from fastapi import HTTPException
from backend.app.services.defect_service import DefectService
from backend.app.repositories.defect_repository import DefectRepository
from backend.app.core.database import init_db

@pytest.fixture(autouse=True)
def setup_db():
    init_db()

@pytest.fixture
def fresh_defect():
    uid = f"DEF-UNIT-{uuid.uuid4().hex[:6].upper()}"
    return DefectRepository.create({
        "defect_id": uid,
        "title": "Unit test isolated fixture defect",
        "description": "Deterministic unit test fixture description",
        "severity": "HIGH",
        "priority": "P2",
        "affected_component": "test-service",
        "environment": "TEST",
        "status": "OPEN",
        "reproduction_status": "PENDING",
        "verification_status": "UNVERIFIED",
        "assigned_owner": "test.owner"
    })

def test_valid_defect_transitions(fresh_defect):
    defect_id = fresh_defect["defect_id"]

    # OPEN -> REPRODUCED should succeed
    res = DefectService.transition_defect(
        defect_id=defect_id,
        target_status="REPRODUCED",
        actor="test.engineer",
        reason="Reproduced with fixture"
    )
    assert res["status"] == "REPRODUCED"

    # REPRODUCED -> INVESTIGATING should succeed
    res = DefectService.transition_defect(
        defect_id=defect_id,
        target_status="INVESTIGATING",
        actor="test.engineer",
        reason="Investigation begun"
    )
    assert res["status"] == "INVESTIGATING"

def test_invalid_transition_rejected(fresh_defect):
    defect_id = fresh_defect["defect_id"]

    # Transitioning directly from OPEN to CLOSED is forbidden
    with pytest.raises(HTTPException) as exc:
        DefectService.transition_defect(
            defect_id=defect_id,
            target_status="CLOSED",
            actor="test.engineer",
            reason="Illegal skip"
        )
    assert exc.value.status_code == 422
    assert "Invalid state transition" in exc.value.detail

def test_cannot_mark_verified_without_verification():
    uid = f"DEF-VERIF-{uuid.uuid4().hex[:6].upper()}"
    DefectRepository.create({
        "defect_id": uid,
        "title": "Unit test defect for verification gate",
        "description": "Test defect description",
        "severity": "LOW",
        "priority": "P4",
        "affected_component": "test-comp",
        "environment": "TEST",
        "status": "VALIDATION_REQUIRED",
        "verification_status": "UNVERIFIED",
        "assigned_owner": "test.owner"
    })

    with pytest.raises(HTTPException) as exc:
        DefectService.transition_defect(
            defect_id=uid,
            target_status="VERIFIED",
            actor="test.engineer",
            reason="Attempted verification bypass"
        )
    assert exc.value.status_code == 422
    assert "Verification status must be VERIFIED" in exc.value.detail

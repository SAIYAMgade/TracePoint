from fastapi import APIRouter, HTTPException
from typing import Optional, List

from ..schemas.releases import (
    ReleaseCreate, ReleaseResponse, ReleaseCheckResponse,
    ReleaseCheckUpdate, ReadinessEvaluationResponse
)
from ..repositories.release_repository import ReleaseRepository
from ..services.release_service import ReleaseService

router = APIRouter(prefix="/releases", tags=["Releases & Release Readiness"])

@router.get("", response_model=List[ReleaseResponse])
def list_releases():
    return ReleaseRepository.get_all()

@router.get("/{release_id}", response_model=ReleaseResponse)
def get_release(release_id: str):
    rel = ReleaseRepository.get_by_id(release_id)
    if not rel:
        raise HTTPException(status_code=404, detail=f"Release {release_id} not found")
    return rel

@router.get("/{release_id}/checks", response_model=List[ReleaseCheckResponse])
def get_release_checks(release_id: str):
    rel = ReleaseRepository.get_by_id(release_id)
    if not rel:
        raise HTTPException(status_code=404, detail=f"Release {release_id} not found")
    return ReleaseRepository.get_checks(release_id)

@router.put("/{release_id}/checks/{check_id}", response_model=ReleaseCheckResponse)
def update_release_check(release_id: str, check_id: str, payload: ReleaseCheckUpdate):
    rel = ReleaseRepository.get_by_id(release_id)
    if not rel:
        raise HTTPException(status_code=404, detail=f"Release {release_id} not found")

    updated = ReleaseRepository.update_check(check_id, payload.model_dump())
    if not updated:
        raise HTTPException(status_code=404, detail=f"Check {check_id} not found")

    # Automatically re-evaluate readiness after check update
    ReleaseService.evaluate_readiness(release_id)

    return updated

@router.post("/{release_id}/evaluate", response_model=ReadinessEvaluationResponse)
def evaluate_release(release_id: str):
    return ReleaseService.evaluate_readiness(release_id)

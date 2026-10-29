from fastapi import APIRouter, HTTPException
from typing import Optional, List

from ..schemas.database_changes import (
    DatabaseChangeResponse, DBChangeValidationResult
)
from ..repositories.db_change_repository import DBChangeRepository
from ..services.db_change_service import DBChangeService

router = APIRouter(prefix="/database-changes", tags=["Database Changes & Validation"])

@router.get("", response_model=List[DatabaseChangeResponse])
def list_database_changes():
    return DBChangeRepository.get_all()

@router.get("/{change_id}", response_model=DatabaseChangeResponse)
def get_database_change(change_id: str):
    chg = DBChangeRepository.get_by_id(change_id)
    if not chg:
        raise HTTPException(status_code=404, detail=f"Database change {change_id} not found")
    return chg

@router.post("/{change_id}/execute", response_model=DBChangeValidationResult)
def execute_migration(change_id: str, applied_by: str = "dba.engineer"):
    return DBChangeService.execute_validation_migration(change_id, applied_by)

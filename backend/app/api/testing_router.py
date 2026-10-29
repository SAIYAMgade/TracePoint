from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from ..schemas.testing import (
    RegressionTestCreate, RegressionTestResponse,
    ExecuteTestRequest, TestRunResponse
)
from ..repositories.testing_repository import TestingRepository
from ..services.test_runner_service import TestRunnerService, ALLOWLISTED_COMMANDS

router = APIRouter(prefix="/testing", tags=["Testing & Test Runs"])

@router.get("/tests", response_model=List[RegressionTestResponse])
def list_regression_tests():
    return TestingRepository.get_all_tests()

@router.get("/tests/{test_id}", response_model=RegressionTestResponse)
def get_regression_test(test_id: str):
    test = TestingRepository.get_test_by_id(test_id)
    if not test:
        raise HTTPException(status_code=404, detail=f"Regression test {test_id} not found")
    return test

@router.get("/runs", response_model=List[TestRunResponse])
def list_test_runs(
    limit: int = Query(50, ge=1, le=100),
    related_defect_id: Optional[str] = None,
    related_release_id: Optional[str] = None
):
    return TestingRepository.get_test_runs(
        limit=limit,
        related_defect_id=related_defect_id,
        related_release_id=related_release_id
    )

@router.get("/allowlist")
def get_allowed_commands():
    return {
        "allowed_commands": list(ALLOWLISTED_COMMANDS.keys()),
        "suites": ALLOWLISTED_COMMANDS
    }

@router.post("/runs/execute", response_model=TestRunResponse)
def execute_test(payload: ExecuteTestRequest):
    if not payload.command:
        raise HTTPException(status_code=400, detail="Command must be specified.")

    return TestRunnerService.execute_test(
        command=payload.command,
        related_defect_id=payload.related_defect_id,
        related_release_id=payload.related_release_id,
        triggered_by=payload.triggered_by
    )

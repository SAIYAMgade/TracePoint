from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum

class ReleaseStatusEnum(str, Enum):
    DRAFT = "DRAFT"
    VALIDATION_IN_PROGRESS = "VALIDATION_IN_PROGRESS"
    BLOCKED = "BLOCKED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    APPROVED = "APPROVED"
    RELEASED = "RELEASED"
    ROLLED_BACK = "ROLLED_BACK"

class CheckStatusEnum(str, Enum):
    PENDING = "PENDING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    WAIVED = "WAIVED"

class ReleaseCheckResponse(BaseModel):
    check_id: str
    release_id: str
    check_name: str
    check_category: str
    is_mandatory: bool
    status: CheckStatusEnum
    waiver_reason: Optional[str] = None
    verified_at: Optional[Any] = None
    verified_by: Optional[str] = None
    evidence_details: Optional[str] = None

class ReleaseCheckUpdate(BaseModel):
    status: CheckStatusEnum
    waiver_reason: Optional[str] = None
    verified_by: str = Field(..., min_length=2, max_length=100)
    evidence_details: Optional[str] = None

class ReleaseBase(BaseModel):
    version_tag: str = Field(..., min_length=2, max_length=50)
    summary: str = Field(..., min_length=5)
    rollback_plan: Optional[str] = None

class ReleaseCreate(ReleaseBase):
    release_id: str = Field(..., min_length=3, max_length=32)

class ReleaseResponse(ReleaseBase):
    release_id: str
    status: ReleaseStatusEnum
    is_ready: bool
    readiness_score: float
    created_at: Any
    updated_at: Any
    released_at: Optional[Any] = None
    checks: Optional[List[ReleaseCheckResponse]] = []

class ReadinessEvaluationResponse(BaseModel):
    release_id: str
    is_ready: bool
    readiness_score: float
    status: ReleaseStatusEnum
    blocking_reasons: List[str]
    evaluated_at: Any

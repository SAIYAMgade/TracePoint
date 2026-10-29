from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class SeverityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class PriorityEnum(str, Enum):
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"
    P4 = "P4"

class DefectStatusEnum(str, Enum):
    OPEN = "OPEN"
    REPRODUCED = "REPRODUCED"
    INVESTIGATING = "INVESTIGATING"
    FIX_PROPOSED = "FIX_PROPOSED"
    VALIDATION_REQUIRED = "VALIDATION_REQUIRED"
    VERIFIED = "VERIFIED"
    CLOSED = "CLOSED"
    REJECTED = "REJECTED"
    DUPLICATE = "DUPLICATE"
    INCONCLUSIVE = "INCONCLUSIVE"

class ReproductionOutcomeEnum(str, Enum):
    PENDING = "PENDING"
    REPRODUCED = "REPRODUCED"
    NOT_REPRODUCED = "NOT_REPRODUCED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REQUIRES_MORE_INFO = "REQUIRES_MORE_INFO"

class VerificationStatusEnum(str, Enum):
    UNVERIFIED = "UNVERIFIED"
    IN_PROGRESS = "IN_PROGRESS"
    VERIFIED = "VERIFIED"
    FAILED = "FAILED"

class DefectBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    description: str = Field(..., min_length=10)
    severity: SeverityEnum
    priority: PriorityEnum
    affected_component: str = Field(..., min_length=2, max_length=100)
    environment: str = Field(..., min_length=2, max_length=50)
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    root_cause_explanation: Optional[str] = None
    proposed_correction: Optional[str] = None
    assigned_owner: str = Field(..., min_length=2, max_length=100)
    associated_regression_test_id: Optional[str] = None
    associated_release_id: Optional[str] = None

class DefectCreate(DefectBase):
    pass

class DefectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[SeverityEnum] = None
    priority: Optional[PriorityEnum] = None
    affected_component: Optional[str] = None
    environment: Optional[str] = None
    expected_behavior: Optional[str] = None
    actual_behavior: Optional[str] = None
    root_cause_explanation: Optional[str] = None
    proposed_correction: Optional[str] = None
    verification_status: Optional[VerificationStatusEnum] = None
    assigned_owner: Optional[str] = None
    associated_regression_test_id: Optional[str] = None
    associated_release_id: Optional[str] = None

class DefectTransitionRequest(BaseModel):
    target_status: DefectStatusEnum
    actor: str = Field(..., min_length=2, max_length=100)
    reason: str = Field(..., min_length=5, max_length=1000)

class DefectResponse(DefectBase):
    defect_id: str
    status: DefectStatusEnum
    reproduction_status: ReproductionOutcomeEnum
    verification_status: VerificationStatusEnum
    created_at: Any
    updated_at: Any
    resolved_at: Optional[Any] = None

class DefectListResponse(BaseModel):
    items: List[DefectResponse]
    total: int
    page: int
    page_size: int

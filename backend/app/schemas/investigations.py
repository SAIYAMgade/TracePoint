from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum

class InvestigationStatusEnum(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    ROOT_CAUSE_IDENTIFIED = "ROOT_CAUSE_IDENTIFIED"
    VERIFIED = "VERIFIED"
    INCONCLUSIVE = "INCONCLUSIVE"
    CLOSED = "CLOSED"

class InvestigationBase(BaseModel):
    problem_statement: str = Field(..., min_length=5)
    observed_symptoms: str = Field(..., min_length=5)
    initial_hypothesis: str = Field(..., min_length=5)
    candidate_causes: Optional[str] = None
    confirmed_root_cause: Optional[str] = None
    proposed_correction: Optional[str] = None
    regression_risk: Optional[str] = None
    verification_plan: Optional[str] = None
    final_conclusion: Optional[str] = None
    status: InvestigationStatusEnum = InvestigationStatusEnum.IN_PROGRESS
    lead_investigator: str = Field(..., min_length=2, max_length=100)

class InvestigationCreate(InvestigationBase):
    defect_id: str = Field(..., min_length=3, max_length=32)

class InvestigationUpdate(BaseModel):
    problem_statement: Optional[str] = None
    observed_symptoms: Optional[str] = None
    initial_hypothesis: Optional[str] = None
    candidate_causes: Optional[str] = None
    confirmed_root_cause: Optional[str] = None
    proposed_correction: Optional[str] = None
    regression_risk: Optional[str] = None
    verification_plan: Optional[str] = None
    final_conclusion: Optional[str] = None
    status: Optional[InvestigationStatusEnum] = None
    lead_investigator: Optional[str] = None

class InvestigationEventCreate(BaseModel):
    event_type: str = Field(..., min_length=2, max_length=50)
    title: str = Field(..., min_length=3, max_length=255)
    details: Optional[str] = None
    actor: str = Field(..., min_length=2, max_length=100)

class InvestigationEventResponse(InvestigationEventCreate):
    event_id: str
    investigation_id: str
    created_at: Any

class InvestigationResponse(InvestigationBase):
    investigation_id: str
    defect_id: str
    created_at: Any
    updated_at: Any
    events: Optional[List[InvestigationEventResponse]] = []

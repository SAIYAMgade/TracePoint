from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum

class FrequencyEnum(str, Enum):
    ALWAYS = "ALWAYS"
    INTERMITTENT = "INTERMITTENT"
    ONCE = "ONCE"

class OutcomeEnum(str, Enum):
    REPRODUCED = "REPRODUCED"
    NOT_REPRODUCED = "NOT_REPRODUCED"
    INCONCLUSIVE = "INCONCLUSIVE"
    REQUIRES_MORE_INFO = "REQUIRES_MORE_INFO"

class ReproductionCreate(BaseModel):
    defect_id: str = Field(..., min_length=3, max_length=32)
    preconditions: Optional[str] = None
    environment_info: Optional[str] = None
    app_version: Optional[str] = None
    steps: List[str] = Field(..., min_length=1)
    synthetic_fixture_ref: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    error_message: Optional[str] = None
    frequency: FrequencyEnum = FrequencyEnum.ALWAYS
    outcome: OutcomeEnum
    notes: Optional[str] = None
    executed_by: str = Field(..., min_length=2, max_length=100)

class ReproductionResponse(BaseModel):
    reproduction_id: str
    defect_id: str
    preconditions: Optional[str] = None
    environment_info: Optional[str] = None
    app_version: Optional[str] = None
    steps: List[str]
    synthetic_fixture_ref: Optional[str] = None
    expected_result: Optional[str] = None
    actual_result: Optional[str] = None
    error_message: Optional[str] = None
    frequency: FrequencyEnum
    outcome: OutcomeEnum
    notes: Optional[str] = None
    executed_by: str
    created_at: Any

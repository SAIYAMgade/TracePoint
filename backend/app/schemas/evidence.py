from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum

class EvidenceTypeEnum(str, Enum):
    ERROR_LOG = "ERROR_LOG"
    STACK_TRACE = "STACK_TRACE"
    SQL_STATEMENT = "SQL_STATEMENT"
    DB_OBJECT = "DB_OBJECT"
    TEST_OUTPUT = "TEST_OUTPUT"
    CODE_DIFF = "CODE_DIFF"
    SYSTEM_METRIC = "SYSTEM_METRIC"

class EvidenceCreate(BaseModel):
    defect_id: str = Field(..., min_length=3, max_length=32)
    investigation_id: Optional[str] = None
    evidence_type: EvidenceTypeEnum
    title: str = Field(..., min_length=3, max_length=255)
    error_code: Optional[str] = None
    sanitized_payload: str = Field(..., min_length=5)
    component: Optional[str] = None
    environment: Optional[str] = None
    correlation_id: Optional[str] = None
    collected_by: str = Field(..., min_length=2, max_length=100)

class EvidenceResponse(EvidenceCreate):
    evidence_id: str
    created_at: Any

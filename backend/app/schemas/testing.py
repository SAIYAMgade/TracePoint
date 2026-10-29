from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum

class TestCategoryEnum(str, Enum):
    UNIT = "UNIT"
    API = "API"
    DATABASE_INTEGRATION = "DATABASE_INTEGRATION"
    REGRESSION = "REGRESSION"
    END_TO_END = "END_TO_END"

class TestOutcomeEnum(str, Enum):
    PASSED = "PASSED"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    NOT_RUN = "NOT_RUN"

class RegressionTestBase(BaseModel):
    test_id: str = Field(..., min_length=3, max_length=32)
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=5)
    test_category: TestCategoryEnum
    related_defect_id: Optional[str] = None
    preconditions: Optional[str] = None
    expected_behavior: str = Field(..., min_length=5)
    execution_command: str = Field(..., min_length=3, max_length=255)

class RegressionTestCreate(RegressionTestBase):
    pass

class RegressionTestResponse(RegressionTestBase):
    last_outcome: TestOutcomeEnum
    last_run_at: Optional[Any] = None
    created_at: Any

class ExecuteTestRequest(BaseModel):
    command: Optional[str] = None
    related_defect_id: Optional[str] = None
    related_release_id: Optional[str] = None
    triggered_by: str = Field(default="developer", min_length=2, max_length=100)

class TestRunResponse(BaseModel):
    run_id: str
    test_suite_id: str
    execution_method: str
    command: str
    outcome: str
    passed_count: int
    failed_count: int
    skipped_count: int
    duration_ms: int
    output_summary: Optional[str] = None
    environment_meta: Optional[str] = None
    related_defect_id: Optional[str] = None
    related_release_id: Optional[str] = None
    triggered_by: str
    started_at: Any
    completed_at: Any

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from enum import Enum

class DBChangeStatusEnum(str, Enum):
    PENDING = "PENDING"
    VALIDATED = "VALIDATED"
    APPLIED = "APPLIED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"

class DBChangeTypeEnum(str, Enum):
    TABLE_DDL = "TABLE_DDL"
    INDEX_DDL = "INDEX_DDL"
    CONSTRAINT_DDL = "CONSTRAINT_DDL"
    PLSQL_PACKAGE = "PLSQL_PACKAGE"
    PLSQL_PROCEDURE = "PLSQL_PROCEDURE"
    DATA_MIGRATION = "DATA_MIGRATION"

class DatabaseChangeCreate(BaseModel):
    change_id: str = Field(..., min_length=3, max_length=32)
    change_name: str = Field(..., min_length=3, max_length=100)
    change_type: DBChangeTypeEnum
    target_schema: str = Field(..., min_length=2, max_length=50)
    sql_script: str = Field(..., min_length=5)
    rollback_script: Optional[str] = None
    pre_check_query: Optional[str] = None
    post_check_query: Optional[str] = None
    oracle_object_name: Optional[str] = None

class DatabaseChangeResponse(DatabaseChangeCreate):
    status: DBChangeStatusEnum
    execution_log: Optional[str] = None
    applied_at: Optional[Any] = None
    applied_by: Optional[str] = None

class DBChangeValidationResult(BaseModel):
    change_id: str
    pre_check_passed: bool
    applied_successfully: bool
    post_check_passed: bool
    execution_log: str
    timestamp: Any

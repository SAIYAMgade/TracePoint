from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SeverityCount(BaseModel):
    severity: str
    count: int

class DashboardMetrics(BaseModel):
    open_defects_by_severity: Dict[str, int]
    defects_awaiting_reproduction: int
    investigations_without_root_cause: int
    fixes_awaiting_verification: int
    failed_regression_tests: int
    releases_blocked: int
    reopened_defects_count: int
    avg_resolution_hours: Optional[float] = None
    total_active_defects: int
    total_verified_defects: int

class ReportQueryResponse(BaseModel):
    report_name: str
    description: str
    sql_source: str
    columns: List[str]
    rows: List[Dict[str, Any]]

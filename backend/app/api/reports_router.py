from fastapi import APIRouter, HTTPException
from typing import Dict, Any

from ..schemas.reports import DashboardMetrics, ReportQueryResponse
from ..repositories.report_repository import ReportRepository

router = APIRouter(prefix="/reports", tags=["Reports & Analytics"])

@router.get("/dashboard", response_model=DashboardMetrics)
def get_dashboard_summary():
    return ReportRepository.get_dashboard_metrics()

@router.get("/view/{report_name}", response_model=ReportQueryResponse)
def get_report_view(report_name: str):
    return ReportRepository.get_report_data(report_name)

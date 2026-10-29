from fastapi import APIRouter
from typing import Dict, Any

from ..core.database import db_manager
from ..core.config import settings

router = APIRouter(prefix="/health", tags=["System Health & Diagnostics"])

@router.get("")
def get_system_health():
    db_health = db_manager.get_health()
    return {
        "status": "HEALTHY",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database": db_health,
        "tracepoint_lab_active": True,
        "supported_test_runner": "pytest allowlisted process isolation"
    }

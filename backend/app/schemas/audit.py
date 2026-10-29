from pydantic import BaseModel
from typing import Optional, Any

class AuditLogResponse(BaseModel):
    audit_id: str
    entity_type: str
    entity_id: str
    action: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    actor: str
    correlation_id: Optional[str] = None
    created_at: Any

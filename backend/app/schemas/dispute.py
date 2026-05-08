from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.dispute import DisputeStatus, DisputeResolution

class DisputeCreateRequest(BaseModel):
    pass  # No body needed, inferred from contract

class DisputeResolveRequest(BaseModel):
    resolution: DisputeResolution
    comment: str

class DisputeMessageCreateRequest(BaseModel):
    content: str
    file_url: Optional[str] = None

class DisputeMessageResponse(BaseModel):
    id: str
    author_id: str
    content: str
    file_url: Optional[str]
    created_at: datetime

class DisputeResponse(BaseModel):
    id: str
    contract_id: str
    initiated_by_id: str
    status: DisputeStatus
    resolution: Optional[DisputeResolution]
    resolution_comment: Optional[str]
    resolved_by_id: Optional[str]
    resolved_at: Optional[datetime]
    messages: List[DisputeMessageResponse]

class DisputeListResponse(BaseModel):
    disputes: List[DisputeResponse]
    total: int
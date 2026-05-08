from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.notification import NotificationType

class NotificationResponse(BaseModel):
    id: str
    type: NotificationType
    title: str
    message: str
    is_read: bool
    created_at: datetime
    related_entity_type: Optional[str]
    related_entity_id: Optional[str]

class NotificationListResponse(BaseModel):
    notifications: List[NotificationResponse]
    total: int
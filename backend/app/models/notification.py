from enum import Enum
from sqlalchemy import String, Text, Boolean, ForeignKey, UUID, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class NotificationType(str, Enum):
    contract = "contract"
    payment = "payment"
    dispute = "dispute"
    system = "system"

class Notification(Base):
    __tablename__ = "notifications"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType))
    title: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    related_entity_type: Mapped[str] = mapped_column(String, nullable=True)
    related_entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="notifications")
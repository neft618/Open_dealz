from sqlalchemy import String, JSON, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class AuditLog(Base):
    __tablename__ = "audit_log"

    entity_type: Mapped[str] = mapped_column(String)
    entity_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True))
    action: Mapped[str] = mapped_column(String)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=True)
    tx_hash: Mapped[str] = mapped_column(String(64), unique=True)

    user: Mapped["User"] = relationship("User", back_populates="audit_logs")
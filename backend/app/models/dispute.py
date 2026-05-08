from enum import Enum
from sqlalchemy import String, Text, ForeignKey, DateTime, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.models.base import Base

class DisputeStatus(str, Enum):
    open = "open"
    under_review = "under_review"
    resolved = "resolved"

class DisputeResolution(str, Enum):
    executor = "executor"
    customer = "customer"
    shared = "shared"

class Dispute(Base):
    __tablename__ = "disputes"

    contract_id: Mapped[UUID] = mapped_column(ForeignKey("contracts.id"), unique=True)
    initiated_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[DisputeStatus] = mapped_column(SQLEnum(DisputeStatus), default=DisputeStatus.open)
    resolution: Mapped[DisputeResolution] = mapped_column(SQLEnum(DisputeResolution), nullable=True)
    resolution_comment: Mapped[str] = mapped_column(Text, nullable=True)
    resolved_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)
    resolved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="dispute")
    initiated_by: Mapped["User"] = relationship("User", foreign_keys=[initiated_by_id])
    resolved_by: Mapped["User"] = relationship("User", foreign_keys=[resolved_by_id])
    messages: Mapped[List["DisputeMessage"]] = relationship("DisputeMessage", back_populates="dispute", order_by="DisputeMessage.created_at")

class DisputeMessage(Base):
    __tablename__ = "dispute_messages"

    dispute_id: Mapped[UUID] = mapped_column(ForeignKey("disputes.id"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    file_url: Mapped[str] = mapped_column(String, nullable=True)

    dispute: Mapped["Dispute"] = relationship("Dispute", back_populates="messages")
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id])
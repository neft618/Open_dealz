from enum import Enum
from sqlalchemy import String, Text, Date, Numeric, ForeignKey, Integer, CheckConstraint, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.models.base import Base

class OrderStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"
    cancelled = "cancelled"

class ApplicationStatus(str, Enum):
    pending = "pending"
    accepted = "accepted"
    rejected = "rejected"

class Application(Base):
    __tablename__ = "applications"

    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"))
    executor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    cover_letter: Mapped[str] = mapped_column(Text)
    proposed_price: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[ApplicationStatus] = mapped_column(SQLEnum(ApplicationStatus), default=ApplicationStatus.pending)

    order: Mapped["Order"] = relationship("Order", back_populates="applications")
    executor: Mapped["User"] = relationship("User", back_populates="applications")

    __table_args__ = (
        CheckConstraint('proposed_price > 0', name='check_proposed_price_positive'),
    )
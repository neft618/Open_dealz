from sqlalchemy import String, Text, Date, Numeric, ForeignKey, Integer, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.models.base import Base

class OrderStatus(str, SQLEnum):
    open = "open"
    in_progress = "in_progress"
    closed = "closed"
    cancelled = "cancelled"

class Order(Base):
    __tablename__ = "orders"

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[OrderStatus] = mapped_column(SQLEnum(OrderStatus), default=OrderStatus.open)
    budget: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    deadline: Mapped[Date] = mapped_column(Date)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    executor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), nullable=True)

    customer: Mapped["User"] = relationship("User", foreign_keys=[customer_id], back_populates="orders")
    executor: Mapped["User"] = relationship("User", foreign_keys=[executor_id], back_populates="contracts_as_executor")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="order")
    contract: Mapped["Contract"] = relationship("Contract", back_populates="order", uselist=False)

class ApplicationStatus(str, SQLEnum):
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
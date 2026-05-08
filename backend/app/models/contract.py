from enum import Enum
from sqlalchemy import String, Text, Date, Numeric, ForeignKey, Boolean, DateTime, Integer, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.models.base import Base

class ContractStatus(str, Enum):
    draft = "draft"
    signed = "signed"
    in_progress = "in_progress"
    completed = "completed"
    disputed = "disputed"
    cancelled = "cancelled"

class PaymentType(str, Enum):
    fixed = "fixed"
    hourly = "hourly"
    milestone = "milestone"

class ClauseType(str, Enum):
    subject_description = "subject_description"
    timeline = "timeline"
    payment_terms = "payment_terms"
    termination_conditions = "termination_conditions"
    result_review_period = "result_review_period"
    refund_policy = "refund_policy"
    platform_commission = "platform_commission"
    ip_rights = "ip_rights"
    confidentiality = "confidentiality"

class ContractClause(Base):
    __tablename__ = "contract_clauses"

    contract_id: Mapped[UUID] = mapped_column(ForeignKey("contracts.id"))
    clause_type: Mapped[ClauseType] = mapped_column(SQLEnum(ClauseType))
    content: Mapped[str] = mapped_column(Text)
    position: Mapped[int] = mapped_column(Integer)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="clauses")

class MilestoneStatus(str, SQLEnum):
    pending = "pending"
    in_progress = "in_progress"
    approved = "approved"
    rejected = "rejected"

class Milestone(Base):
    __tablename__ = "milestones"

    contract_id: Mapped[UUID] = mapped_column(ForeignKey("contracts.id"))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    deadline: Mapped[Date] = mapped_column(Date)
    status: Mapped[MilestoneStatus] = mapped_column(SQLEnum(MilestoneStatus), default=MilestoneStatus.pending)
    position: Mapped[int] = mapped_column(Integer)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="milestones")
    deliverables: Mapped[List["Deliverable"]] = relationship("Deliverable", back_populates="milestone")

class Deliverable(Base):
    __tablename__ = "deliverables"

    contract_id: Mapped[UUID] = mapped_column(ForeignKey("contracts.id"))
    milestone_id: Mapped[UUID] = mapped_column(ForeignKey("milestones.id"), nullable=True)
    file_url: Mapped[str] = mapped_column(String)
    file_name: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    submitted_by_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    contract: Mapped["Contract"] = relationship("Contract", back_populates="deliverables")
    milestone: Mapped["Milestone"] = relationship("Milestone", back_populates="deliverables")
    submitted_by: Mapped["User"] = relationship("User", foreign_keys=[submitted_by_id])
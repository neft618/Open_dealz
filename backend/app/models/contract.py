from sqlalchemy import String, Text, Date, Numeric, ForeignKey, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.models.base import Base

class ContractStatus(str, SQLEnum):
    draft = "draft"
    signed = "signed"
    in_progress = "in_progress"
    completed = "completed"
    disputed = "disputed"
    cancelled = "cancelled"

class PaymentType(str, SQLEnum):
    fixed = "fixed"
    hourly = "hourly"
    milestone = "milestone"

class Contract(Base):
    __tablename__ = "contracts"

    order_id: Mapped[UUID] = mapped_column(ForeignKey("orders.id"), unique=True)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    executor_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    status: Mapped[ContractStatus] = mapped_column(SQLEnum(ContractStatus), default=ContractStatus.draft)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    platform_fee: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    payment_type: Mapped[PaymentType] = mapped_column(SQLEnum(PaymentType))
    signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    customer_signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    executor_signed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="contract")
    customer: Mapped["User"] = relationship("User", foreign_keys=[customer_id], back_populates="contracts_as_customer")
    executor: Mapped["User"] = relationship("User", foreign_keys=[executor_id], back_populates="contracts_as_executor")
    clauses: Mapped[List["ContractClause"]] = relationship("ContractClause", back_populates="contract", order_by="ContractClause.position")
    milestones: Mapped[List["Milestone"]] = relationship("Milestone", back_populates="contract", order_by="Milestone.position")
    deliverables: Mapped[List["Deliverable"]] = relationship("Deliverable", back_populates="contract")
    escrow_transactions: Mapped[List["EscrowTransaction"]] = relationship("EscrowTransaction", back_populates="contract")
    dispute: Mapped["Dispute"] = relationship("Dispute", back_populates="contract", uselist=False)

class ClauseType(str, SQLEnum):
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
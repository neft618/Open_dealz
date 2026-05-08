from sqlalchemy import String, Numeric, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class EscrowTransactionType(str, SQLEnum):
    lock = "lock"
    release = "release"
    refund = "refund"
    fee = "fee"

class EscrowTransactionStatus(str, SQLEnum):
    pending = "pending"
    confirmed = "confirmed"
    failed = "failed"

class InitiatedBy(str, SQLEnum):
    customer = "customer"
    executor = "executor"
    system = "system"

class EscrowTransaction(Base):
    __tablename__ = "escrow_transactions"

    contract_id: Mapped[UUID] = mapped_column(ForeignKey("contracts.id"))
    type: Mapped[EscrowTransactionType] = mapped_column(SQLEnum(EscrowTransactionType))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    status: Mapped[EscrowTransactionStatus] = mapped_column(SQLEnum(EscrowTransactionStatus), default=EscrowTransactionStatus.pending)
    initiated_by: Mapped[InitiatedBy] = mapped_column(SQLEnum(InitiatedBy))
    tx_hash: Mapped[str] = mapped_column(String, unique=True)
    metadata_: Mapped[dict] = mapped_column(JSON, nullable=True)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="escrow_transactions")
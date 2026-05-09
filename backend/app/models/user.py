from enum import Enum
from sqlalchemy import String, Boolean, Integer, Text, Enum as SQLEnum, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.models.base import Base

class UserRole(str, Enum):
    customer = "customer"
    executor = "executor"
    admin = "admin"

class Specialization(str, Enum):
    web_development = "web_development"
    mobile_development = "mobile_development"
    data_science = "data_science"
    design = "design"
    marketing = "marketing"
    other = "other"

class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String)
    full_name: Mapped[str] = mapped_column(String)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), default=UserRole.customer)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    wallet_address: Mapped[str] = mapped_column(String(42), nullable=True)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False)
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")
    applications: Mapped[List["Application"]] = relationship("Application", back_populates="executor")
    contracts_as_customer: Mapped[List["Contract"]] = relationship("Contract", foreign_keys="Contract.customer_id", back_populates="customer")
    contracts_as_executor: Mapped[List["Contract"]] = relationship("Contract", foreign_keys="Contract.executor_id", back_populates="executor")
    disputes_initiated: Mapped[List["Dispute"]] = relationship("Dispute", back_populates="initiated_by")
    notifications: Mapped[List["Notification"]] = relationship("Notification", back_populates="user")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="user")

class Profile(Base):
    __tablename__ = "profiles"

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), unique=True)
    bio: Mapped[str] = mapped_column(Text, nullable=True)
    specialization: Mapped[Specialization] = mapped_column(SQLEnum(Specialization), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="profile")
    skills: Mapped[List["ProfileSkill"]] = relationship("ProfileSkill", back_populates="profile")
    portfolios: Mapped[List["Portfolio"]] = relationship("Portfolio", back_populates="profile")

class Portfolio(Base):
    __tablename__ = "portfolios"

    profile_id: Mapped[UUID] = mapped_column(ForeignKey("profiles.id"))
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    file_url: Mapped[str] = mapped_column(String)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="portfolios")
from sqlalchemy import SmallInteger, Text, ForeignKey, UUID, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List
from app.models.base import Base

class Review(Base):
    __tablename__ = "reviews"

    contract_id: Mapped[UUID] = mapped_column(ForeignKey("contracts.id"))
    author_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    recipient_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    rating: Mapped[int] = mapped_column(SmallInteger)
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    contract: Mapped["Contract"] = relationship("Contract", back_populates="reviews")
    author: Mapped["User"] = relationship("User", foreign_keys=[author_id])
    recipient: Mapped["User"] = relationship("User", foreign_keys=[recipient_id])

    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        UniqueConstraint('contract_id', 'author_id', name='unique_contract_author_review'),
    )
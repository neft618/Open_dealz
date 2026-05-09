from sqlalchemy import String, ForeignKey, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class ProfileSkill(Base):
    __tablename__ = "profile_skills"

    profile_id: Mapped[UUID] = mapped_column(ForeignKey("profiles.id"))
    skill: Mapped[str] = mapped_column(String)

    profile: Mapped["Profile"] = relationship("Profile", back_populates="skills")
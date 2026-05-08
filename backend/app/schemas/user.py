from pydantic import BaseModel, EmailStr
from typing import Optional, List
from app.models.user import UserRole, Specialization

class ProfileUpdateRequest(BaseModel):
    bio: Optional[str] = None
    skills: Optional[str] = None
    specialization: Optional[Specialization] = None

class RoleUpdateRequest(BaseModel):
    role: UserRole

class PortfolioItem(BaseModel):
    id: str
    title: str
    description: Optional[str]
    file_url: str

class ProfileResponse(BaseModel):
    id: str
    user_id: str
    bio: Optional[str]
    skills: Optional[str]
    specialization: Optional[Specialization]
    rating: int
    contracts_count: int
    portfolio: List[PortfolioItem]

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_verified: bool
    is_active: bool
    profile: Optional[ProfileResponse]
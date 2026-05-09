from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, UploadFile
from app.models.user import User, Profile, Portfolio
from app.models.audit import AuditLog
from app.schemas.user import ProfileUpdateRequest, RoleUpdateRequest, PortfolioItem, ProfileResponse
from app.core.security import generate_tx_hash
from app.core.storage import upload_file, delete_file
from datetime import datetime, UTC
from uuid import uuid4
import os

async def get_public_profile(db: AsyncSession, user_id: str) -> ProfileResponse:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile = user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    portfolio_items = [
        PortfolioItem(
            id=str(p.id),
            title=p.title,
            description=p.description,
            file_url=p.file_url
        ) for p in profile.portfolios
    ]

    return ProfileResponse(
        id=str(profile.id),
        user_id=str(profile.user_id),
        bio=profile.bio,
        skills=profile.skills,
        specialization=profile.specialization,
        rating=profile.rating,
        contracts_count=profile.contracts_count,
        portfolio=portfolio_items
    )

async def update_profile(db: AsyncSession, user_id: str, data: ProfileUpdateRequest, current_user: User):
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    if data.bio is not None:
        profile.bio = data.bio
    if data.skills is not None:
        profile.skills = data.skills
    if data.specialization is not None:
        profile.specialization = data.specialization

    await db.commit()

async def update_role(db: AsyncSession, user_id: str, data: RoleUpdateRequest, current_user: User):
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if current_user.role == "admin":
        raise HTTPException(status_code=400, detail="Cannot change admin role")

    current_user.role = data.role
    await db.commit()

async def upload_portfolio_item(db: AsyncSession, user_id: str, file: UploadFile, title: str, description: str, current_user: User):
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    profile = current_user.profile
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Generate filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{user_id}/{uuid4()}{ext}"

    # Upload to storage
    file_bytes = await file.read()
    public_url = await upload_file("portfolios", filename, file_bytes, file.content_type)

    # Save to DB
    portfolio_item = Portfolio(
        profile_id=profile.id,
        title=title,
        description=description,
        file_url=public_url
    )
    db.add(portfolio_item)
    await db.commit()
    await db.refresh(portfolio_item)

async def delete_portfolio_item(db: AsyncSession, user_id: str, portfolio_id: str, current_user: User):
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id, Portfolio.profile_id == current_user.profile.id))
    portfolio_item = result.scalar_one_or_none()
    if not portfolio_item:
        raise HTTPException(status_code=404, detail="Portfolio item not found")

    # Delete from storage
    path = portfolio_item.file_url.split("/")[-1]  # Assuming URL ends with path
    await delete_file("portfolios", path)

    # Delete from DB
    await db.delete(portfolio_item)
    await db.commit()
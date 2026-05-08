from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.user import ProfileResponse, ProfileUpdateRequest, RoleUpdateRequest
from app.services.user_service import get_public_profile, update_profile, update_role, upload_portfolio_item, delete_portfolio_item
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(user_id: str, db: AsyncSession = Depends(get_db)):
    return await get_public_profile(db, user_id)

@router.patch("/me/profile")
async def update_user_profile(
    data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await update_profile(db, str(current_user.id), data, current_user)
    return {"message": "Profile updated"}

@router.patch("/me/role")
async def update_user_role(
    data: RoleUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await update_role(db, str(current_user.id), data, current_user)
    return {"message": "Role updated"}

@router.post("/me/portfolio")
async def upload_portfolio(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await upload_portfolio_item(db, str(current_user.id), file, title, description, current_user)
    return {"message": "Portfolio item uploaded"}

@router.delete("/me/portfolio/{portfolio_id}")
async def delete_portfolio(
    portfolio_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await delete_portfolio_item(db, str(current_user.id), portfolio_id, current_user)
    return {"message": "Portfolio item deleted"}
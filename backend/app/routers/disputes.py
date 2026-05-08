from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.dispute import DisputeResponse, DisputeMessageCreateRequest, DisputeResolveRequest
from app.services.dispute_service import open_dispute, get_dispute, add_dispute_message, set_dispute_under_review, resolve_dispute
from app.dependencies import get_current_active_user, require_admin
from app.models.user import User
from typing import Optional

router = APIRouter()

@router.post("/")
async def create_dispute(
    contract_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await open_dispute(db, contract_id, str(current_user.id))
    return {"message": "Dispute opened"}

@router.get("/{dispute_id}", response_model=DisputeResponse)
async def get_dispute_detail(
    dispute_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_dispute(db, dispute_id, str(current_user.id))

@router.post("/{dispute_id}/messages")
async def add_message_to_dispute(
    dispute_id: str,
    content: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    data = DisputeMessageCreateRequest(content=content)
    await add_dispute_message(db, dispute_id, data, file, str(current_user.id))
    return {"message": "Message added"}

@router.patch("/{dispute_id}/status")
async def update_dispute_status(
    dispute_id: str,
    status: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    if status == "under_review":
        await set_dispute_under_review(db, dispute_id, str(current_user.id))
    return {"message": "Status updated"}

@router.post("/{dispute_id}/resolve")
async def resolve_dispute_endpoint(
    dispute_id: str,
    data: DisputeResolveRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    await resolve_dispute(db, dispute_id, data, str(current_user.id))
    return {"message": "Dispute resolved"}
from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.contract import ContractResponse, ContractUpdateRequest, ContractClauseUpdate, MilestoneCreateRequest
from app.services.contract_service import get_contract, update_contract, bulk_update_clauses, sign_contract, add_milestone, update_milestone_status, upload_deliverable, get_deliverable_download_url, accept_work, reject_work
from app.dependencies import get_current_active_user
from app.models.user import User
from typing import List, Optional

router = APIRouter()

@router.get("/{contract_id}", response_model=ContractResponse)
async def get_contract_detail(
    contract_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_contract(db, contract_id, str(current_user.id))

@router.patch("/{contract_id}")
async def update_contract_detail(
    contract_id: str,
    data: ContractUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await update_contract(db, contract_id, data, str(current_user.id))
    return {"message": "Contract updated"}

@router.patch("/{contract_id}/clauses")
async def update_contract_clauses(
    contract_id: str,
    clauses: List[ContractClauseUpdate],
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await bulk_update_clauses(db, contract_id, clauses, str(current_user.id))
    return {"message": "Clauses updated"}

@router.post("/{contract_id}/sign")
async def sign_contract_endpoint(
    contract_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await sign_contract(db, contract_id, str(current_user.id))
    return {"message": "Contract signed"}

@router.post("/{contract_id}/milestones")
async def add_contract_milestone(
    contract_id: str,
    data: MilestoneCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    milestone = await add_milestone(db, contract_id, data, str(current_user.id))
    return {"id": str(milestone.id), "message": "Milestone added"}

@router.patch("/{contract_id}/milestones/{milestone_id}")
async def update_milestone(
    contract_id: str,
    milestone_id: str,
    status: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await update_milestone_status(db, contract_id, milestone_id, status, str(current_user.id))
    return {"message": "Milestone updated"}

@router.post("/{contract_id}/deliverables")
async def upload_contract_deliverable(
    contract_id: str,
    file: UploadFile = File(...),
    description: str = Form(...),
    milestone_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    deliverable = await upload_deliverable(db, contract_id, file, description, milestone_id, str(current_user.id))
    return {"id": str(deliverable.id), "message": "Deliverable uploaded"}

@router.get("/{contract_id}/deliverables/{deliverable_id}/download")
async def download_deliverable(
    contract_id: str,
    deliverable_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    signed_url = await get_deliverable_download_url(db, contract_id, deliverable_id, str(current_user.id))
    return {"url": signed_url}

@router.post("/{contract_id}/accept")
async def accept_contract_work(
    contract_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await accept_work(db, contract_id, str(current_user.id))
    return {"message": "Work accepted, funds released"}

@router.post("/{contract_id}/reject")
async def reject_contract_work(
    contract_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await reject_work(db, contract_id, str(current_user.id))
    return {"message": "Work rejected, dispute opened"}
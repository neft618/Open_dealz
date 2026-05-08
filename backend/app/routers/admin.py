from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select, func, update
from app.core.database import get_db
from app.dependencies import require_admin
from app.models.user import User
from app.models.contract import Contract
from app.models.dispute import Dispute
from app.models.escrow import EscrowTransaction
from app.models.audit import AuditLog
from typing import List, Optional

router = APIRouter()

@router.get("/contracts")
async def get_admin_contracts(
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    query = select(Contract)
    if status:
        query = query.where(Contract.status == status)
    if search:
        query = query.where(Contract.id.ilike(f"%{search}%"))

    total = await db.execute(select(func.count()).select_from(query.subquery()))
    contracts = await db.execute(query.offset(skip).limit(limit))
    return {"contracts": [c.__dict__ for c in contracts.scalars()], "total": total.scalar()}

@router.get("/disputes")
async def get_admin_disputes(
    status: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    query = select(Dispute)
    if status:
        query = query.where(Dispute.status == status)

    total = await db.execute(select(func.count()).select_from(query.subquery()))
    disputes = await db.execute(query.offset(skip).limit(limit))
    return {"disputes": [d.__dict__ for d in disputes.scalars()], "total": total.scalar()}

@router.get("/users")
async def get_admin_users(
    search: Optional[str] = Query(None),
    role: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    query = select(User)
    if search:
        query = query.where(User.email.ilike(f"%{search}%"))
    if role:
        query = query.where(User.role == role)

    total = await db.execute(select(func.count()).select_from(query.subquery()))
    users = await db.execute(query.offset(skip).limit(limit))
    return {"users": [u.__dict__ for u in users.scalars()], "total": total.scalar()}

@router.patch("/users/{user_id}/verify")
async def verify_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True
    await db.commit()
    return {"message": "User verified"}

@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_active = False
    await db.commit()
    return {"message": "User deactivated"}

@router.get("/metrics")
async def get_admin_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    # Simplified metrics
    total_contracts = await db.execute(select(func.count(Contract.id)))
    active_contracts = await db.execute(select(func.count(Contract.id)).where(Contract.status == "in_progress"))
    completed_contracts = await db.execute(select(func.count(Contract.id)).where(Contract.status == "completed"))
    cancelled_contracts = await db.execute(select(func.count(Contract.id)).where(Contract.status == "cancelled"))

    total_disputes = await db.execute(select(func.count(Dispute.id)))
    open_disputes = await db.execute(select(func.count(Dispute.id)).where(Dispute.status == "open"))
    resolved_disputes = await db.execute(select(func.count(Dispute.id)).where(Dispute.status == "resolved"))

    commission_result = await db.execute(select(func.sum(EscrowTransaction.amount)).where(EscrowTransaction.type == "fee"))
    total_commission = commission_result.scalar() or 0

    avg_amount_result = await db.execute(select(func.avg(Contract.total_amount)))
    avg_contract_amount = avg_amount_result.scalar() or 0

    new_users_30 = await db.execute(select(func.count(User.id)).where(User.created_at >= func.now() - func.interval('30 days')))

    return {
        "total_contracts": total_contracts.scalar(),
        "active_contracts": active_contracts.scalar(),
        "completed_contracts": completed_contracts.scalar(),
        "cancelled_contracts": cancelled_contracts.scalar(),
        "total_disputes": total_disputes.scalar(),
        "open_disputes": open_disputes.scalar(),
        "resolved_disputes": resolved_disputes.scalar(),
        "dispute_resolution_rate": resolved_disputes.scalar() / max(total_disputes.scalar(), 1),
        "total_commission_collected": total_commission,
        "avg_contract_amount": avg_contract_amount,
        "success_rate": completed_contracts.scalar() / max(total_contracts.scalar(), 1),
        "new_users_last_30_days": new_users_30.scalar()
    }

@router.get("/audit-log")
async def get_admin_audit_log(
    entity_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    skip: int = Query(0),
    limit: int = Query(20),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    query = select(AuditLog)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if action:
        query = query.where(AuditLog.action == action)

    total = await db.execute(select(func.count()).select_from(query.subquery()))
    logs = await db.execute(query.offset(skip).limit(limit).order_by(AuditLog.created_at.desc()))
    return {"logs": [l.__dict__ for l in logs.scalars()], "total": total.scalar()}
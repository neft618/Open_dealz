from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, UploadFile
from app.models.dispute import Dispute, DisputeMessage
from app.models.contract import Contract
from app.models.audit import AuditLog
from app.schemas.dispute import DisputeResponse, DisputeMessageCreateRequest, DisputeResolveRequest
from app.services.escrow_service import release_funds, refund_funds
from app.services.notification_service import notify
from app.core.security import generate_tx_hash
from app.core.storage import upload_file
from datetime import datetime, UTC
from uuid import uuid4
import os
from typing import List

async def open_dispute(db: AsyncSession, contract_id: str, user_id: str):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract or contract.status != "in_progress":
        raise HTTPException(status_code=400, detail="Contract not available for dispute")

    if str(contract.customer_id) != user_id and str(contract.executor_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if dispute already exists
    existing = await db.execute(select(Dispute).where(Dispute.contract_id == contract_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Dispute already exists")

    dispute = Dispute(
        contract_id=contract_id,
        initiated_by_id=user_id,
        status="open"
    )
    db.add(dispute)
    contract.status = "disputed"

    # Audit
    audit = AuditLog(
        entity_type="dispute",
        entity_id=dispute.id,
        action="open",
        user_id=user_id,
        payload={"contract_id": contract_id},
        tx_hash=generate_tx_hash(str(dispute.id), "open", {"contract_id": contract_id}, datetime.now(UTC))
    )
    db.add(audit)

    await db.commit()
    await db.refresh(dispute)

    # Notify admins and parties
    admins = await db.execute(select(User.id).where(User.role == "admin"))
    admin_ids = [str(row[0]) for row in admins.all()]
    for admin_id in admin_ids:
        await notify(db, admin_id, "dispute", "New Dispute", f"Dispute opened for contract {contract_id}")

    await notify(db, str(contract.customer_id), "dispute", "Dispute Opened", f"Dispute opened for contract {contract_id}")
    await notify(db, str(contract.executor_id), "dispute", "Dispute Opened", f"Dispute opened for contract {contract_id}")

async def get_dispute(db: AsyncSession, dispute_id: str, user_id: str) -> DisputeResponse:
    result = await db.execute(
        select(Dispute)
        .where(Dispute.id == dispute_id)
        .options(selectinload(Dispute.messages).selectinload(DisputeMessage.author))
    )
    dispute = result.scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    contract = dispute.contract
    if str(contract.customer_id) != user_id and str(contract.executor_id) != user_id and user_id not in [str(row[0]) for row in await db.execute(select(User.id).where(User.role == "admin"))]:
        raise HTTPException(status_code=403, detail="Not authorized")

    messages = [
        DisputeMessageResponse(
            id=str(m.id),
            author_id=str(m.author_id),
            content=m.content,
            file_url=m.file_url,
            created_at=m.created_at
        ) for m in dispute.messages
    ]

    return DisputeResponse(
        id=str(dispute.id),
        contract_id=str(dispute.contract_id),
        initiated_by_id=str(dispute.initiated_by_id),
        status=dispute.status,
        resolution=dispute.resolution,
        resolution_comment=dispute.resolution_comment,
        resolved_by_id=str(dispute.resolved_by_id) if dispute.resolved_by_id else None,
        resolved_at=dispute.resolved_at,
        messages=messages
    )

async def add_dispute_message(db: AsyncSession, dispute_id: str, data: DisputeMessageCreateRequest, file: Optional[UploadFile], user_id: str):
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    if not dispute:
        raise HTTPException(status_code=404, detail="Dispute not found")

    contract = dispute.contract
    if str(contract.customer_id) != user_id and str(contract.executor_id) != user_id and user_id not in [str(row[0]) for row in await db.execute(select(User.id).where(User.role == "admin"))]:
        raise HTTPException(status_code=403, detail="Not authorized")

    file_url = None
    if file:
        ext = os.path.splitext(file.filename)[1]
        filename = f"disputes/{dispute_id}/{uuid4()}{ext}"
        file_bytes = await file.read()
        file_url = await upload_file("deliverables", filename, file_bytes, file.content_type)

    message = DisputeMessage(
        dispute_id=dispute_id,
        author_id=user_id,
        content=data.content,
        file_url=file_url
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    # Notify others
    parties = [str(contract.customer_id), str(contract.executor_id)]
    admins = [str(row[0]) for row in (await db.execute(select(User.id).where(User.role == "admin"))).all()]
    recipients = list(set(parties + admins))
    recipients.remove(user_id)

    for recipient in recipients:
        await notify(db, recipient, "dispute", "New Dispute Message", f"New message in dispute {dispute_id}")

async def set_dispute_under_review(db: AsyncSession, dispute_id: str, user_id: str):
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    if not dispute or dispute.status != "open":
        raise HTTPException(status_code=400, detail="Dispute not available")

    # Check admin
    result = await db.execute(select(User).where(User.id == user_id, User.role == "admin"))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Admin required")

    dispute.status = "under_review"
    await db.commit()

async def resolve_dispute(db: AsyncSession, dispute_id: str, data: DisputeResolveRequest, user_id: str):
    result = await db.execute(select(Dispute).where(Dispute.id == dispute_id))
    dispute = result.scalar_one_or_none()
    if not dispute or dispute.status not in ["open", "under_review"]:
        raise HTTPException(status_code=400, detail="Dispute not resolvable")

    # Check admin
    result = await db.execute(select(User).where(User.id == user_id, User.role == "admin"))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Admin required")

    contract = dispute.contract
    now = datetime.now(UTC)

    if data.resolution == "executor":
        await release_funds(db, str(contract.id))
    elif data.resolution == "customer":
        await refund_funds(db, str(contract.id))
    elif data.resolution == "shared":
        # Custom logic for split, assume 50/50
        half = contract.total_amount / 2
        # This would need custom escrow logic, for now assume release half and refund half
        pass  # Implement custom escrow split

    dispute.status = "resolved"
    dispute.resolution = data.resolution
    dispute.resolution_comment = data.comment
    dispute.resolved_by_id = user_id
    dispute.resolved_at = now
    contract.status = "completed"  # Or based on resolution

    # Audit
    audit = AuditLog(
        entity_type="dispute",
        entity_id=dispute.id,
        action="resolve",
        user_id=user_id,
        payload={"dispute_id": dispute_id, "resolution": data.resolution.value},
        tx_hash=generate_tx_hash(dispute_id, "resolve", {"dispute_id": dispute_id, "resolution": data.resolution.value}, now)
    )
    db.add(audit)

    await db.commit()

    # Notify parties
    await notify(db, str(contract.customer_id), "dispute", "Dispute Resolved", f"Dispute {dispute_id} has been resolved")
    await notify(db, str(contract.executor_id), "dispute", "Dispute Resolved", f"Dispute {dispute_id} has been resolved")
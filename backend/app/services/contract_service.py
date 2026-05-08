from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, UploadFile
from app.models.contract import Contract, ContractClause, Milestone, Deliverable
from app.models.escrow import EscrowTransaction
from app.models.audit import AuditLog
from app.schemas.contract import ContractResponse, ContractUpdateRequest, ContractClauseUpdate, MilestoneCreateRequest, DeliverableResponse
from app.services.escrow_service import lock_funds, release_funds, refund_funds
from app.services.notification_service import notify
from app.core.security import generate_tx_hash
from app.core.storage import upload_file, get_signed_url
from datetime import datetime, UTC
from uuid import uuid4
import os

async def get_contract(db: AsyncSession, contract_id: str, user_id: str) -> ContractResponse:
    result = await db.execute(
        select(Contract)
        .where(Contract.id == contract_id)
        .options(
            selectinload(Contract.clauses),
            selectinload(Contract.milestones),
            selectinload(Contract.deliverables)
        )
    )
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    # Check permission
    if str(contract.customer_id) != user_id and str(contract.executor_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    clauses = [
        ContractClauseResponse(
            id=str(c.id),
            clause_type=c.clause_type,
            content=c.content,
            position=c.position,
            is_mandatory=c.is_mandatory
        ) for c in sorted(contract.clauses, key=lambda x: x.position)
    ]

    milestones = [
        MilestoneResponse(
            id=str(m.id),
            title=m.title,
            description=m.description,
            amount=m.amount,
            deadline=m.deadline,
            status=m.status.value,
            position=m.position
        ) for m in sorted(contract.milestones, key=lambda x: x.position)
    ]

    deliverables = [
        DeliverableResponse(
            id=str(d.id),
            file_url=d.file_url,
            file_name=d.file_name,
            file_size=d.file_size,
            description=d.description,
            submitted_at=d.submitted_at
        ) for d in contract.deliverables
    ]

    return ContractResponse(
        id=str(contract.id),
        order_id=str(contract.order_id),
        customer_id=str(contract.customer_id),
        executor_id=str(contract.executor_id),
        status=contract.status,
        total_amount=contract.total_amount,
        platform_fee=contract.platform_fee,
        payment_type=contract.payment_type,
        signed_at=contract.signed_at,
        clauses=clauses,
        milestones=milestones,
        deliverables=deliverables
    )

async def update_contract(db: AsyncSession, contract_id: str, data: ContractUpdateRequest, user_id: str):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract or contract.status != ContractStatus.draft:
        raise HTTPException(status_code=400, detail="Contract not editable")

    if str(contract.customer_id) != user_id and str(contract.executor_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if data.payment_type:
        contract.payment_type = data.payment_type
    if data.total_amount:
        contract.total_amount = data.total_amount

    await db.commit()

async def bulk_update_clauses(db: AsyncSession, contract_id: str, clauses: List[ContractClauseUpdate], user_id: str):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    if str(contract.customer_id) != user_id and str(contract.executor_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    for clause_data in clauses:
        result = await db.execute(select(ContractClause).where(ContractClause.id == clause_data.id, ContractClause.contract_id == contract_id))
        clause = result.scalar_one_or_none()
        if clause:
            clause.content = clause_data.content
            clause.position = clause_data.position

    await db.commit()

async def sign_contract(db: AsyncSession, contract_id: str, user_id: str):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")

    now = datetime.now(UTC)
    if str(contract.customer_id) == user_id:
        contract.customer_signed_at = now
    elif str(contract.executor_id) == user_id:
        contract.executor_signed_at = now
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if both signed
    if contract.customer_signed_at and contract.executor_signed_at:
        contract.status = ContractStatus.in_progress
        contract.signed_at = now
        contract.platform_fee = contract.total_amount * 0.03  # Assuming 3%

        # Lock funds
        await lock_funds(db, contract_id, contract.total_amount)

    # Audit log
    audit = AuditLog(
        entity_type="contract",
        entity_id=contract.id,
        action="sign",
        user_id=user_id,
        payload={"contract_id": contract_id},
        tx_hash=generate_tx_hash(contract_id, "sign", {"contract_id": contract_id}, now)
    )
    db.add(audit)

    await db.commit()

    # Notify
    await notify(db, str(contract.customer_id), "contract", "Contract Signed", f"Contract {contract_id} has been signed")
    await notify(db, str(contract.executor_id), "contract", "Contract Signed", f"Contract {contract_id} has been signed")

async def add_milestone(db: AsyncSession, contract_id: str, data: MilestoneCreateRequest, user_id: str):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract or contract.status != ContractStatus.in_progress or str(contract.executor_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    max_position = await db.execute(select(func.max(Milestone.position)).where(Milestone.contract_id == contract_id))
    position = (max_position.scalar() or 0) + 1

    milestone = Milestone(
        contract_id=contract_id,
        title=data.title,
        description=data.description,
        amount=data.amount,
        deadline=data.deadline,
        position=position
    )
    db.add(milestone)
    await db.commit()
    await db.refresh(milestone)
    return milestone

async def update_milestone_status(db: AsyncSession, contract_id: str, milestone_id: str, status: str, user_id: str):
    result = await db.execute(select(Milestone).where(Milestone.id == milestone_id, Milestone.contract_id == contract_id))
    milestone = result.scalar_one_or_none()
    if not milestone:
        raise HTTPException(status_code=404, detail="Milestone not found")

    contract = milestone.contract
    if str(contract.executor_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    milestone.status = status
    await db.commit()

async def upload_deliverable(db: AsyncSession, contract_id: str, file: UploadFile, description: str, milestone_id: Optional[str], user_id: str):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract or contract.status != ContractStatus.in_progress or str(contract.executor_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Upload file
    ext = os.path.splitext(file.filename)[1]
    filename = f"{contract_id}/{uuid4()}{ext}"
    file_bytes = await file.read()
    public_url = await upload_file("deliverables", filename, file_bytes, file.content_type)

    # Save deliverable
    deliverable = Deliverable(
        contract_id=contract_id,
        milestone_id=milestone_id,
        file_url=public_url,
        file_name=file.filename,
        file_size=len(file_bytes),
        description=description,
        submitted_by_id=user_id
    )
    db.add(deliverable)
    await db.commit()
    await db.refresh(deliverable)

    # Notify customer
    await notify(db, str(contract.customer_id), "contract", "New Deliverable", f"A new deliverable has been submitted for contract {contract_id}")

    return deliverable

async def get_deliverable_download_url(db: AsyncSession, contract_id: str, deliverable_id: str, user_id: str) -> str:
    result = await db.execute(select(Deliverable).where(Deliverable.id == deliverable_id, Deliverable.contract_id == contract_id))
    deliverable = result.scalar_one_or_none()
    if not deliverable:
        raise HTTPException(status_code=404, detail="Deliverable not found")

    contract = deliverable.contract
    if str(contract.customer_id) != user_id and str(contract.executor_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Get signed URL for private bucket
    path = deliverable.file_url.split("/")[-1]
    signed_url = await get_signed_url("deliverables", path)
    return signed_url

async def accept_work(db: AsyncSession, contract_id: str, user_id: str):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract or contract.status != ContractStatus.in_progress or str(contract.customer_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Release funds
    await release_funds(db, contract_id)

    # Update contract
    contract.status = ContractStatus.completed

    # Update profiles
    customer_profile = contract.customer.profile
    executor_profile = contract.executor.profile
    if customer_profile:
        customer_profile.contracts_count += 1
    if executor_profile:
        executor_profile.contracts_count += 1
        executor_profile.rating += 1  # Simple rating increase

    # Audit
    audit = AuditLog(
        entity_type="contract",
        entity_id=contract.id,
        action="complete",
        user_id=user_id,
        payload={"contract_id": contract_id},
        tx_hash=generate_tx_hash(contract_id, "complete", {"contract_id": contract_id}, datetime.now(UTC))
    )
    db.add(audit)

    await db.commit()

    # Notify
    await notify(db, str(contract.executor_id), "contract", "Contract Completed", f"Contract {contract_id} has been completed")

async def reject_work(db: AsyncSession, contract_id: str, user_id: str):
    result = await db.execute(select(Contract).where(Contract.id == contract_id))
    contract = result.scalar_one_or_none()
    if not contract or contract.status != ContractStatus.in_progress or str(contract.customer_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    contract.status = ContractStatus.disputed

    # Audit
    audit = AuditLog(
        entity_type="contract",
        entity_id=contract.id,
        action="dispute",
        user_id=user_id,
        payload={"contract_id": contract_id},
        tx_hash=generate_tx_hash(contract_id, "dispute", {"contract_id": contract_id}, datetime.now(UTC))
    )
    db.add(audit)

    await db.commit()

    # Notify
    await notify(db, str(contract.executor_id), "contract", "Contract Disputed", f"Contract {contract_id} has been disputed")
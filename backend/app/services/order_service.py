from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy import func
from fastapi import HTTPException
from app.models.order import Order, Application
from app.models.contract import Contract, ContractClause, ClauseType
from app.models.audit import AuditLog
from app.schemas.order import OrderCreateRequest, OrderResponse, ApplicationCreateRequest, ApplicationResponse, AcceptApplicationRequest
from app.core.security import generate_tx_hash
from datetime import datetime, UTC
from typing import List, Optional
from decimal import Decimal

async def create_order(db: AsyncSession, data: OrderCreateRequest, customer_id: str) -> Order:
    order = Order(
        title=data.title,
        description=data.description,
        budget=data.budget,
        deadline=data.deadline,
        customer_id=customer_id
    )
    db.add(order)
    await db.commit()
    await db.refresh(order)
    return order

async def list_orders(
    db: AsyncSession,
    status: Optional[str] = None,
    min_budget: Optional[Decimal] = None,
    max_budget: Optional[Decimal] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 10
) -> tuple[List[Order], int]:
    query = select(Order)

    if status:
        query = query.where(Order.status == status)
    if min_budget:
        query = query.where(Order.budget >= min_budget)
    if max_budget:
        query = query.where(Order.budget <= max_budget)
    if search:
        query = query.where(Order.title.ilike(f"%{search}%"))

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    orders = result.scalars().all()

    return orders, total

async def get_order_detail(db: AsyncSession, order_id: str, user_id: str) -> Order:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Check permission: owner or executor
    if str(order.customer_id) != user_id and str(order.executor_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return order

async def update_order(db: AsyncSession, order_id: str, data: OrderCreateRequest, user_id: str):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order or str(order.customer_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    if order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Order is not open")

    order.title = data.title
    order.description = data.description
    order.budget = data.budget
    order.deadline = data.deadline

    await db.commit()

async def cancel_order(db: AsyncSession, order_id: str, user_id: str):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order or str(order.customer_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    order.status = OrderStatus.cancelled
    await db.commit()

async def apply_to_order(db: AsyncSession, order_id: str, data: ApplicationCreateRequest, executor_id: str):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order or order.status != OrderStatus.open:
        raise HTTPException(status_code=400, detail="Order not available")

    # Check if already applied
    existing = await db.execute(select(Application).where(Application.order_id == order_id, Application.executor_id == executor_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already applied")

    application = Application(
        order_id=order_id,
        executor_id=executor_id,
        cover_letter=data.cover_letter,
        proposed_price=data.proposed_price
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    return application

async def list_applications(db: AsyncSession, order_id: str, user_id: str) -> List[Application]:
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order or str(order.customer_id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(select(Application).where(Application.order_id == order_id))
    return result.scalars().all()

async def accept_application(db: AsyncSession, order_id: str, application_id: str, user_id: str):
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order or str(order.customer_id) != user_id or order.status != OrderStatus.open:
        raise HTTPException(status_code=403, detail="Not authorized")

    result = await db.execute(select(Application).where(Application.id == application_id, Application.order_id == order_id))
    application = result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Update applications
    await db.execute(
        Application.__table__.update()
        .where(Application.order_id == order_id)
        .values(status=ApplicationStatus.rejected)
    )
    application.status = ApplicationStatus.accepted

    # Update order
    order.executor_id = application.executor_id
    order.status = OrderStatus.in_progress

    # Create contract
    contract = Contract(
        order_id=order.id,
        customer_id=order.customer_id,
        executor_id=application.executor_id,
        total_amount=application.proposed_price,
        payment_type="fixed"  # Default
    )
    db.add(contract)
    await db.flush()

    # Create default clauses
    clauses = []
    for i, clause_type in enumerate(ClauseType):
        clause = ContractClause(
            contract_id=contract.id,
            clause_type=clause_type,
            content="",
            position=i,
            is_mandatory=True
        )
        clauses.append(clause)
    db.add_all(clauses)

    await db.commit()
    return str(contract.id)
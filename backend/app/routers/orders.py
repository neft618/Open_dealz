from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.order import OrderCreateRequest, OrderResponse, OrderListResponse, ApplicationCreateRequest, ApplicationResponse, AcceptApplicationRequest
from app.services.order_service import create_order, list_orders, get_order_detail, update_order, cancel_order, apply_to_order, list_applications, accept_application
from app.dependencies import get_current_active_user
from app.models.user import User
from typing import Optional
from decimal import Decimal

router = APIRouter()

@router.post("/", response_model=dict)
async def create_new_order(
    data: OrderCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role not in ["customer", "admin"]:
        raise HTTPException(status_code=403, detail="Only customers can create orders")

    order = await create_order(db, data, str(current_user.id))
    return {"id": str(order.id), "message": "Order created"}

@router.get("/", response_model=OrderListResponse)
async def get_orders(
    status: Optional[str] = Query(None),
    min_budget: Optional[Decimal] = Query(None),
    max_budget: Optional[Decimal] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    orders, total = await list_orders(db, status, min_budget, max_budget, search, skip, limit)
    order_responses = [
        OrderResponse(
            id=str(o.id),
            title=o.title,
            description=o.description,
            status=o.status,
            budget=o.budget,
            deadline=o.deadline,
            customer_id=str(o.customer_id),
            executor_id=str(o.executor_id) if o.executor_id else None,
            application_count=len(o.applications)
        ) for o in orders
    ]
    return OrderListResponse(orders=order_responses, total=total)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    order = await get_order_detail(db, order_id, str(current_user.id))
    return OrderResponse(
        id=str(order.id),
        title=order.title,
        description=order.description,
        status=order.status,
        budget=order.budget,
        deadline=order.deadline,
        customer_id=str(order.customer_id),
        executor_id=str(order.executor_id) if order.executor_id else None,
        application_count=len(order.applications)
    )

@router.patch("/{order_id}")
async def update_existing_order(
    order_id: str,
    data: OrderCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await update_order(db, order_id, data, str(current_user.id))
    return {"message": "Order updated"}

@router.delete("/{order_id}")
async def cancel_existing_order(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    await cancel_order(db, order_id, str(current_user.id))
    return {"message": "Order cancelled"}

@router.post("/{order_id}/applications", response_model=dict)
async def apply_to_existing_order(
    order_id: str,
    data: ApplicationCreateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    if current_user.role not in ["executor", "admin"]:
        raise HTTPException(status_code=403, detail="Only executors can apply")

    application = await apply_to_order(db, order_id, data, str(current_user.id))
    return {"id": str(application.id), "message": "Application submitted"}

@router.get("/{order_id}/applications", response_model=List[ApplicationResponse])
async def get_order_applications(
    order_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    applications = await list_applications(db, order_id, str(current_user.id))
    return [
        ApplicationResponse(
            id=str(a.id),
            order_id=str(a.order_id),
            executor_id=str(a.executor_id),
            cover_letter=a.cover_letter,
            proposed_price=a.proposed_price,
            status=a.status
        ) for a in applications
    ]

@router.post("/{order_id}/applications/{application_id}/accept", response_model=dict)
async def accept_order_application(
    order_id: str,
    application_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    contract_id = await accept_application(db, order_id, application_id, str(current_user.id))
    return {"contract_id": contract_id, "message": "Application accepted, contract created"}
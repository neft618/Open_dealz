from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from decimal import Decimal
from app.models.order import OrderStatus, ApplicationStatus

class OrderCreateRequest(BaseModel):
    title: str
    description: str
    budget: Decimal
    deadline: date

class OrderResponse(BaseModel):
    id: str
    title: str
    description: str
    status: OrderStatus
    budget: Decimal
    deadline: date
    customer_id: str
    executor_id: Optional[str]
    application_count: int

class OrderListResponse(BaseModel):
    orders: List[OrderResponse]
    total: int

class ApplicationCreateRequest(BaseModel):
    cover_letter: str
    proposed_price: Decimal

class ApplicationResponse(BaseModel):
    id: str
    order_id: str
    executor_id: str
    cover_letter: str
    proposed_price: Decimal
    status: ApplicationStatus

class AcceptApplicationRequest(BaseModel):
    application_id: str
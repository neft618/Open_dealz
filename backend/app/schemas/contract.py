from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from app.models.contract import ContractStatus, PaymentType, ClauseType
from app.models.order import OrderStatus
from app.models.order import ApplicationStatus

class ContractClauseUpdate(BaseModel):
    id: str
    content: str
    position: int

class ContractClauseResponse(BaseModel):
    id: str
    clause_type: ClauseType
    content: str
    position: int
    is_mandatory: bool

class MilestoneCreateRequest(BaseModel):
    title: str
    description: Optional[str]
    amount: Decimal
    deadline: date

class MilestoneResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    amount: Decimal
    deadline: date
    status: str
    position: int

class DeliverableResponse(BaseModel):
    id: str
    file_url: str
    file_name: str
    file_size: int
    description: str
    submitted_at: datetime

class ContractResponse(BaseModel):
    id: str
    order_id: str
    customer_id: str
    executor_id: str
    status: ContractStatus
    total_amount: Decimal
    platform_fee: Decimal
    payment_type: PaymentType
    signed_at: Optional[datetime]
    clauses: List[ContractClauseResponse]
    milestones: List[MilestoneResponse]
    deliverables: List[DeliverableResponse]

class ContractUpdateRequest(BaseModel):
    payment_type: Optional[PaymentType] = None
    total_amount: Optional[Decimal] = None
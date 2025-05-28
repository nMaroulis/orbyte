from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .base import ResponseModel

class PaymentStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# Shared properties
class PaymentBase(BaseModel):
    amount: Optional[float] = Field(None, gt=0, description="Amount in mock tokens")
    status: Optional[PaymentStatus] = PaymentStatus.PENDING
    transaction_hash: Optional[str] = None

# Properties to receive on payment creation
class PaymentCreate(PaymentBase):
    task_id: int
    recipient_id: int
    amount: float = Field(..., gt=0, description="Amount in mock tokens")

# Properties to receive on payment update
class PaymentUpdate(PaymentBase):
    status: Optional[PaymentStatus] = None

# Properties shared by models stored in DB
class PaymentInDBBase(PaymentBase):
    id: int
    task_id: int
    payer_id: int
    recipient_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Properties to return to client
class Payment(PaymentInDBBase):
    pass

# Properties stored in DB
class PaymentInDB(PaymentInDBBase):
    pass

# Response models
class PaymentResponse(ResponseModel):
    data: Payment

class PaymentsResponse(ResponseModel):
    data: List[Payment]

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

from .base import ResponseSchema

class FiatCurrency(str, Enum):
    USD = "US Dollar"
    EUR = "Euro"
    GBP = "British Pound"
    CHF = "Swiss Franc"
    JPY = "Japanese Yen"

class FiatWalletStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"

class FiatWalletBase(BaseModel):
    account_number: str = Field(..., description="Bank account number")
    currency: FiatCurrency = Field(FiatCurrency.USD, description="Fiat currency")
    is_primary: bool = Field(False, description="Whether this is the primary wallet")
    bank_name: Optional[str] = Field(None, description="Name of the bank")
    iban: Optional[str] = Field(None, description="International Bank Account Number")
    swift_bic: Optional[str] = Field(None, description="SWIFT/BIC code")

class FiatWalletCreate(FiatWalletBase):
    pass

class FiatWalletUpdate(BaseModel):
    is_primary: Optional[bool] = None
    status: Optional[FiatWalletStatus] = None
    bank_name: Optional[str] = None
    iban: Optional[str] = None
    swift_bic: Optional[str] = None

class FiatWalletInDBBase(FiatWalletBase):
    id: int
    user_id: int
    balance: float = Field(0.0, description="Current wallet balance")
    status: FiatWalletStatus = Field(FiatWalletStatus.ACTIVE, description="Wallet status")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class FiatWalletResponse(ResponseSchema[FiatWalletInDBBase]):
    """Response schema for a single fiat wallet."""
    pass

class FiatWalletListResponse(ResponseSchema[List[FiatWalletInDBBase]]):
    """Response schema for a list of fiat wallets."""
    pass

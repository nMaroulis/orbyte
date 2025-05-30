from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

from .base import ResponseSchema

class CryptoCurrency(str, Enum):
    BTC = "Bitcoin"
    ETH = "Ethereum"
    USDT = "Tether"
    USDC = "USD Coin"
    SOL = "Solana"

class CryptoWalletStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"

class CryptoWalletBase(BaseModel):
    address: str = Field(..., description="Blockchain wallet address")
    currency: CryptoCurrency = Field(..., description="Type of cryptocurrency")
    is_primary: bool = Field(False, description="Whether this is the primary wallet")

class CryptoWalletCreate(CryptoWalletBase):
    pass

class CryptoWalletUpdate(BaseModel):
    is_primary: Optional[bool] = None
    status: Optional[CryptoWalletStatus] = None

class CryptoWalletInDBBase(CryptoWalletBase):
    id: int
    user_id: int
    balance: float = Field(0.0, description="Current wallet balance")
    status: CryptoWalletStatus = Field(CryptoWalletStatus.ACTIVE, description="Wallet status")
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class CryptoWalletResponse(ResponseSchema[CryptoWalletInDBBase]):
    """Response schema for a single crypto wallet."""
    pass

class CryptoWalletListResponse(ResponseSchema[List[CryptoWalletInDBBase]]):
    """Response schema for a list of crypto wallets."""
    pass

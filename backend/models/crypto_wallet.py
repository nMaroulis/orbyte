from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class CryptoCurrency(enum.Enum):
    BTC = "Bitcoin"
    ETH = "Ethereum"
    USDT = "Tether"
    USDC = "USD Coin"
    SOL = "Solana"
    # Add more cryptocurrencies as needed

class CryptoWalletStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"

class CryptoWallet(Base):
    __tablename__ = "crypto_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    address = Column(String, unique=True, index=True, nullable=False)
    currency = Column(Enum(CryptoCurrency), nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(CryptoWalletStatus), default=CryptoWalletStatus.ACTIVE, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="crypto_wallet")

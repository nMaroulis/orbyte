from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, DateTime, func
from sqlalchemy.orm import relationship
from ..database import Base
import enum

class FiatCurrency(enum.Enum):
    USD = "US Dollar"
    EUR = "Euro"
    GBP = "British Pound"
    CHF = "Swiss Franc"
    JPY = "Japanese Yen"
    # Add more fiat currencies as needed

class FiatWalletStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING_VERIFICATION = "pending_verification"
    SUSPENDED = "suspended"

class FiatWallet(Base):
    __tablename__ = "fiat_wallets"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    account_number = Column(String, unique=True, index=True, nullable=False)
    currency = Column(Enum(FiatCurrency), default=FiatCurrency.USD, nullable=False)
    balance = Column(Float, default=0.0, nullable=False)
    status = Column(Enum(FiatWalletStatus), default=FiatWalletStatus.ACTIVE, nullable=False)
    is_primary = Column(Boolean, default=False, nullable=False)
    bank_name = Column(String, nullable=True)
    iban = Column(String, nullable=True)
    swift_bic = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="fiat_wallet")

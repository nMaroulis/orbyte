from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
from .crypto_wallet import CryptoWallet
from .fiat_wallet import FiatWallet

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    wallet_address = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    gpus = relationship("GPU", back_populates="owner")
    tasks = relationship("Task", back_populates="requester")
    payments_made = relationship("Payment", foreign_keys="Payment.payer_id", back_populates="payer")
    payments_received = relationship("Payment", foreign_keys="Payment.recipient_id", back_populates="recipient")
    crypto_wallet = relationship("CryptoWallet", back_populates="user", uselist=False, cascade="all, delete-orphan")
    fiat_wallet = relationship("FiatWallet", back_populates="user", uselist=False, cascade="all, delete-orphan")

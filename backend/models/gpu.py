from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, JSON, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from ..database import Base

# Import the models to ensure they're registered with SQLAlchemy
from .gpu_workflow import GPUWorkflow
from .gpu_model import GPUModel

class GPUStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class GPUModel(str, enum.Enum):
    RTX_3090 = "RTX 3090"
    RTX_4090 = "RTX 4090"
    A100 = "A100"
    H100 = "H100"
    MI250X = "MI250X"
    OTHER = "other"

class GPU(Base):
    __tablename__ = "gpus"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    model = Column(Enum(GPUModel), nullable=False)
    vram_gb = Column(Integer, nullable=False)  # VRAM in GB
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    price_per_hour = Column(Float, nullable=False)  # Price in mock tokens
    status = Column(Enum(GPUStatus), default=GPUStatus.AVAILABLE)
    specs = Column(JSON)  # Additional specs as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="gpus")
    tasks = relationship("Task", back_populates="gpu")
    supported_workflows = relationship("GPUWorkflow", back_populates="gpu", cascade="all, delete-orphan")
    installed_models = relationship("GPUModel", back_populates="gpu", cascade="all, delete-orphan")

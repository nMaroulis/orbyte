from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, JSON, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from ..database import Base

# Import the models to ensure they're registered with SQLAlchemy
from .gpu_workflow import GPUWorkflow
from .llm_model import LLMModel

class GPUStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

class GPU(Base):
    """
    Represents a GPU resource in the system.
    
    Attributes:
        name: User-defined name for the GPU
        model: Hardware model of the GPU (e.g., 'RTX 4090', 'A100')
        vram_gb: Amount of VRAM in GB
        owner_id: ID of the user who owns this GPU
        price_per_hour: Price per hour in mock tokens
        status: Current status of the GPU (available/in_use/maintenance/offline)
        specs: Additional specifications and capabilities of the GPU
    """
    __tablename__ = "gpus"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)  # e.g., 'RTX 4090', 'A100', etc.
    vram_gb = Column(Integer, nullable=False)  # VRAM in GB
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    price_per_hour = Column(Float, nullable=False)  # Price in mock tokens
    status = Column(Enum(GPUStatus), default=GPUStatus.AVAILABLE, index=True)
    specs = Column(JSON, default=dict)  # Additional specs as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="gpus")
    tasks = relationship("Task", back_populates="gpu")
    supported_workflows = relationship(
        "GPUWorkflow", 
        back_populates="gpu", 
        cascade="all, delete-orphan"
    )
    installed_models = relationship(
        "LLMModel", 
        back_populates="gpu", 
        cascade="all, delete-orphan"
    )

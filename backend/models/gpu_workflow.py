from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, JSON, func
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from ..database import Base

class WorkflowType(str, enum.Enum):
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    CODE_GENERATION = "code_generation"
    FINE_TUNING = "fine_tuning"
    OTHER = "other"

class WorkflowStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIGURING = "configuring"
    READY = "ready"
    ERROR = "error"

class GPUWorkflow(Base):
    __tablename__ = "gpu_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    gpu_id = Column(Integer, ForeignKey("gpus.id"), nullable=False)
    workflow_type = Column(Enum(WorkflowType), nullable=False)
    status = Column(Enum(WorkflowStatus), default=WorkflowStatus.PENDING)
    config = Column(JSON, default={})  # Configuration specific to the workflow
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    gpu = relationship("GPU", back_populates="supported_workflows")

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
from ..database import Base

class GPUWorkflow(Base):
    __tablename__ = "gpu_workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    gpu_id = Column(Integer, ForeignKey('gpus.id', ondelete='CASCADE'))
    workflow_type = Column(String, nullable=False)  # e.g., "pytorch_inference", "fine_tuning"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship
    gpu = relationship("GPU", back_populates="supported_workflows")

class GPUModel(Base):
    __tablename__ = "gpu_models"
    
    id = Column(Integer, primary_key=True, index=True)
    gpu_id = Column(Integer, ForeignKey('gpus.id', ondelete='CASCADE'))
    model_name = Column(String, nullable=False)  # e.g., "llama3-7b"
    model_path = Column(String, nullable=True)    # Optional path where model is stored
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    gpu = relationship("GPU", back_populates="installed_models")

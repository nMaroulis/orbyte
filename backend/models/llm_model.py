from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from ..database import Base
from ..schemas.llm_model import LLMModelType

class LLMModel(Base):
    __tablename__ = "llm_models"
    
    id = Column(Integer, primary_key=True, index=True)
    gpu_id = Column(Integer, ForeignKey('gpus.id', ondelete='CASCADE'), nullable=False)
    model_type = Column(String, nullable=False)  # Using LLMModelType enum values
    model_name = Column(String, nullable=False)  # User-friendly name
    model_path = Column(String)                  # Path where model is stored
    model_config = Column(JSON, default={})      # Configuration specific to the model
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    gpu = relationship("GPU", back_populates="installed_models")

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class GPUModel(Base):
    __tablename__ = "gpu_models"
    
    id = Column(Integer, primary_key=True, index=True)
    gpu_id = Column(Integer, ForeignKey("gpus.id"), nullable=False)
    model_name = Column(String, nullable=False)  # Name of the ML model
    model_type = Column(String, nullable=False)  # Type of model (e.g., "llama2", "stablediffusion")
    model_path = Column(String)  # Path to the model files
    model_config = Column(JSON, default={})  # Configuration specific to the model
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    gpu = relationship("GPU", back_populates="installed_models")

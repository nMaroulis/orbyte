from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Enum, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..database import Base

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, enum.Enum):
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    MODEL_TRAINING = "model_training"
    OTHER = "other"

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    task_type = Column(Enum(TaskType), nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gpu_id = Column(Integer, ForeignKey("gpus.id"), nullable=True)
    input_data = Column(JSON)  # Input data for the task
    output_data = Column(JSON)  # Output/result of the task
    cost = Column(Float, default=0.0)  # Cost in mock tokens
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    requester = relationship("User", back_populates="tasks")
    gpu = relationship("GPU", back_populates="tasks")
    payment = relationship("Payment", back_populates="task", uselist=False)

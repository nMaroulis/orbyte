from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .base import ResponseModel

class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskType(str, Enum):
    TEXT_GENERATION = "text_generation"
    IMAGE_GENERATION = "image_generation"
    MODEL_TRAINING = "model_training"
    OTHER = "other"

# Shared properties
class TaskBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[TaskType] = TaskType.OTHER
    input_data: Optional[Dict[str, Any]] = None

# Properties to receive on task creation
class TaskCreate(TaskBase):
    title: str
    task_type: TaskType
    input_data: Dict[str, Any]
    gpu_id: Optional[int] = None  # If not provided, system will assign

# Properties to receive on task update
class TaskUpdate(TaskBase):
    status: Optional[TaskStatus] = None
    output_data: Optional[Dict[str, Any]] = None
    cost: Optional[float] = None

# Properties shared by models stored in DB
class TaskInDBBase(TaskBase):
    id: int
    requester_id: int
    gpu_id: Optional[int] = None
    status: TaskStatus = TaskStatus.PENDING
    cost: float = 0.0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Properties to return to client
class Task(TaskInDBBase):
    output_data: Optional[Dict[str, Any]] = None

# Properties stored in DB
class TaskInDB(TaskInDBBase):
    pass

# Response models
class TaskResponse(ResponseModel):
    data: Task

class TasksResponse(ResponseModel):
    data: List[Task]

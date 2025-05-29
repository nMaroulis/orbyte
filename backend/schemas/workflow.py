from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from .base import ResponseModel
from .llm_model import LLMModelType

class WorkflowType(str, Enum):
    PYTORCH_INFERENCE = "pytorch_inference"
    FINE_TUNING = "fine_tuning"
    ORBYTE_CHATBOT = "orbyte_chatbot"
    TRAINING = "training"
    INFERENCE = "inference"
    EMBEDDING = "embedding"
    MODEL_SERVING = "model_serving"

class GPUWorkflowBase(BaseModel):
    workflow_type: WorkflowType
    is_active: bool = True

class GPUWorkflowCreate(GPUWorkflowBase):
    pass

class GPUWorkflowUpdate(GPUWorkflowBase):
    is_active: Optional[bool] = None

class GPUWorkflowInDBBase(GPUWorkflowBase):
    id: int
    gpu_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class GPUWorkflow(GPUWorkflowInDBBase):
    pass

# LLM Model schemas have been moved to llm_model.py

class GPUWorkflowResponse(ResponseModel):
    data: GPUWorkflow

class GPUWorkflowsResponse(ResponseModel):
    data: List[GPUWorkflow]

class GPUWorkflowConfig(BaseModel):
    """Configuration for GPU workflows and installed models"""
    supported_workflows: List[WorkflowType] = Field(
        default_factory=list,
        description="List of supported workflow types for the GPU"
    )
    installed_models: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of installed models with their configurations"
    )

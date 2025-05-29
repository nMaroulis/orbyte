from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum
from .base import ResponseModel

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

class GPUModelBase(BaseModel):
    model_name: str = Field(..., min_length=1)
    model_path: Optional[str] = None
    is_active: bool = True

class GPUModelCreate(GPUModelBase):
    pass

class GPUModelUpdate(GPUModelBase):
    model_name: Optional[str] = Field(None, min_length=1)
    model_path: Optional[str] = None
    is_active: Optional[bool] = None

class GPUModelInDBBase(GPUModelBase):
    id: int
    gpu_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class GPUModel(GPUModelInDBBase):
    pass

class GPUWorkflowResponse(ResponseModel):
    data: GPUWorkflow

class GPUWorkflowsResponse(ResponseModel):
    data: List[GPUWorkflow]

class GPUModelResponse(ResponseModel):
    data: GPUModel

class GPUModelsResponse(ResponseModel):
    data: List[GPUModel]

class GPUWorkflowConfig(BaseModel):
    supported_workflows: List[WorkflowType]
    installed_models: List[str]

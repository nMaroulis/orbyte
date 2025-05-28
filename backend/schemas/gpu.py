from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .base import ResponseModel

class GPUModel(str, Enum):
    RTX_3090 = "RTX 3090"
    RTX_4090 = "RTX 4090"
    A100 = "A100"
    H100 = "H100"
    MI250X = "MI250X"
    OTHER = "other"

class GPUStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

# Shared properties
class GPUBase(BaseModel):
    name: Optional[str] = None
    model: Optional[GPUModel] = None
    vram_gb: Optional[int] = None
    price_per_hour: Optional[float] = None
    status: Optional[GPUStatus] = GPUStatus.AVAILABLE
    specs: Optional[Dict[str, Any]] = None

# Properties to receive on GPU creation
class GPUCreate(GPUBase):
    name: str
    model: GPUModel
    vram_gb: int = Field(..., gt=0, description="VRAM in GB")
    price_per_hour: float = Field(..., gt=0, description="Price per hour in mock tokens")
    specs: Dict[str, Any] = {}

# Properties to receive on GPU update
class GPUUpdate(GPUBase):
    pass

# Properties shared by models stored in DB
class GPUInDBBase(GPUBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Properties to return to client
class GPU(GPUInDBBase):
    pass

# Properties stored in DB
class GPUInDB(GPUInDBBase):
    pass

# Response models
class GPUResponse(ResponseModel):
    data: GPU

class GPUsResponse(ResponseModel):
    data: List[GPU]

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from .base import ResponseModel
from .llm_model import LLMModelType

class GPUStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"

# Shared properties
class GPUBase(BaseModel):
    name: Optional[str] = Field(
        None, 
        description="User-defined name for the GPU"
    )
    model: Optional[str] = Field(
        None,
        description="Hardware model of the GPU (e.g., 'RTX 4090', 'A100')"
    )
    vram_gb: Optional[int] = Field(
        None,
        gt=0,
        description="Amount of VRAM in GB"
    )
    price_per_hour: Optional[float] = Field(
        None,
        gt=0,
        description="Price per hour in mock tokens"
    )
    status: GPUStatus = Field(
        default=GPUStatus.AVAILABLE,
        description="Current status of the GPU"
    )
    specs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional specifications and capabilities of the GPU"
    )
    # System information
    os: Optional[str] = Field(
        None,
        description="Operating system (e.g., 'Ubuntu 22.04', 'Windows 11')"
    )
    cpu_model: Optional[str] = Field(
        None,
        description="CPU model (e.g., 'AMD Ryzen 9 5950X')"
    )
    cpu_cores: Optional[int] = Field(
        None,
        ge=1,
        description="Total number of CPU logical cores"
    )
    ram_gb: Optional[int] = Field(
        None,
        ge=1,
        description="Total system RAM in GB"
    )
    storage_gb: Optional[int] = Field(
        None,
        ge=1,
        description="Total storage capacity in GB"
    )
    network_speed_mbps: Optional[int] = Field(
        None,
        ge=1,
        description="Network speed in Mbps"
    )

# Properties to receive on GPU creation
class GPUCreate(GPUBase):
    name: str = Field(..., min_length=1, description="Name for the GPU")
    model: str = Field(..., min_length=1, description="Hardware model of the GPU")
    vram_gb: int = Field(..., gt=0, description="Amount of VRAM in GB")
    price_per_hour: float = Field(..., gt=0, description="Price per hour in mock tokens")

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

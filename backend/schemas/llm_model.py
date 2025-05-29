from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class LLMModelType(str, Enum):
    # OpenAI Models
    GPT_4O = "gpt-4o"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4 = "gpt-4"
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    
    # Anthropic Models
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    CLAUDE_3_SONNET = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU = "claude-3-haiku-20240307"
    
    # Meta (Llama) Models
    LLAMA_3_70B = "llama-3-70b"
    LLAMA_3_8B = "llama-3-8b"
    LLAMA_2_70B = "llama-2-70b"
    LLAMA_2_13B = "llama-2-13b"
    LLAMA_2_7B = "llama-2-7b"
    
    # Mistral AI Models
    MIXTRAL_8X7B = "mixtral-8x7b"
    MIXTRAL_8X22B = "mixtral-8x22b"
    MISTRAL_7B = "mistral-7b"
    
    # Google Models
    GEMINI_PRO = "gemini-pro"
    GEMINI_ULTRA = "gemini-ultra"
    
    # Cohere Models
    COMMAND_R_PLUS = "command-r-plus"
    COMMAND_R = "command-r"
    
    # Local/Community Models
    CODE_LLAMA_70B = "codellama-70b"
    PHI_3 = "phi-3"
    DBRX = "dbrx"

class LLMModelBase(BaseModel):
    model_type: LLMModelType
    model_name: str = Field(..., description="User-friendly name for the model")
    model_path: Optional[str] = Field(None, description="Path where the model is stored")
    is_active: bool = True

class LLMModelCreate(LLMModelBase):
    pass

class LLMModelUpdate(BaseModel):
    model_path: Optional[str] = None
    is_active: Optional[bool] = None

class LLMModelInDB(LLMModelBase):
    id: int
    gpu_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class LLMModelResponse(BaseModel):
    success: bool
    message: str
    data: Optional[LLMModelInDB] = None

class LLMModelsResponse(BaseModel):
    success: bool
    message: str
    data: list[LLMModelInDB]

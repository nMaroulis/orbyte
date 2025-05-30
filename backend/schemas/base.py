from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any, TypeVar, Generic
from datetime import datetime
from enum import Enum

T = TypeVar('T')

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class Message(BaseModel):
    detail: str

class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

class SortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"

class ResponseSchema(BaseModel, Generic[T]):
    """
    Base response schema for all API responses.
    """
    success: bool = True
    message: str = "Operation successful"
    data: Optional[T] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
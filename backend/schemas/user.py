from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from .base import ResponseModel

# Shared properties
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    wallet_address: Optional[str] = Field(
        None, 
        description="Ethereum-compatible wallet address (0x...)",
        pattern='^0x[a-fA-F0-9]{40}$'
    )
    is_active: Optional[bool] = True

# Properties to receive on user creation
class UserCreate(UserBase):
    email: EmailStr
    wallet_address: str = Field(
        ..., 
        description="Ethereum-compatible wallet address (0x...)",
        pattern='^0x[a-fA-F0-9]{40}$'
    )
    password: str = Field(..., min_length=8, max_length=100)

# Properties to receive on user update
class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=8, max_length=100)

# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Properties to return to client
class User(UserInDBBase):
    pass

# Properties stored in DB
class UserInDB(UserInDBBase):
    hashed_password: str

# Response models
class UserResponse(ResponseModel):
    data: User

class UsersResponse(ResponseModel):
    data: List[User]

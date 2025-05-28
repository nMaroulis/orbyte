from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from http import HTTPStatus
from sqlalchemy.orm import Session
from typing import Any, Optional
from pydantic import BaseModel, EmailStr

from .. import schemas, models
from ..core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from ..database import get_db

router = APIRouter(tags=["auth"])

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
) -> dict[str, str]:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/register", response_model=schemas.UserResponse)
async def register_user(
    user_in: schemas.UserCreate,
    db: Session = Depends(get_db)
):
    # Check if user already exists
    db_user = db.query(models.User).filter(
        (models.User.email == user_in.email) | 
        (models.User.wallet_address == user_in.wallet_address)
    ).first()
    
    if db_user:
        if db_user.email == user_in.email:
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        elif db_user.wallet_address == user_in.wallet_address:
            raise HTTPException(
                status_code=400,
                detail="Wallet address already registered"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_in.password)
    db_user = models.User(
        email=user_in.email,
        wallet_address=user_in.wallet_address,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "success": True,
        "message": "User registered successfully",
        "data": db_user
    }

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(
    request: Request,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get the local_kw from query parameters if it exists
    local_kw = request.query_params.get("local_kw")
    if local_kw is not None:
        print(f"Received local_kw: {local_kw}")  # For debugging
        
    # The rest of your function continues here
    try:
        print(f"Current user in /me endpoint: {current_user}")
        
        # Convert SQLAlchemy model to Pydantic model
        user_dict = {
            "id": current_user.id,
            "email": current_user.email,
            "wallet_address": current_user.wallet_address,
            "is_active": current_user.is_active,
            "is_admin": current_user.is_admin,
            "created_at": current_user.created_at,
            "updated_at": current_user.updated_at
        }
        
        print(f"User dict: {user_dict}")
        
        # Create response
        response = {
            "success": True,
            "message": "User retrieved successfully",
            "data": user_dict
        }
        
        print(f"Response: {response}")
        return response
        
    except Exception as e:
        print(f"Error in /me endpoint: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    wallet_address: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None

@router.patch("/me", response_model=schemas.UserResponse)
async def update_current_user(
    user_update: UserUpdateRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        update_data = {}
        
        # Check if email is being updated
        if user_update.email and user_update.email != current_user.email:
            # Check if new email is already taken
            existing_user = db.query(models.User).filter(
                models.User.email == user_update.email
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Email already registered"
                )
            update_data["email"] = user_update.email
        
        # Check if wallet address is being updated
        if user_update.wallet_address and user_update.wallet_address != current_user.wallet_address:
            # Check if new wallet address is already taken
            existing_user = db.query(models.User).filter(
                models.User.wallet_address == user_update.wallet_address
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Wallet address already registered"
                )
            update_data["wallet_address"] = user_update.wallet_address
        
        # Check if password is being updated
        if user_update.new_password:
            if not user_update.current_password:
                raise HTTPException(
                    status_code=HTTPStatus.BAD_REQUEST,
                    detail="Current password is required to set a new password"
                )
            
            # Verify current password
            if not authenticate_user(db, current_user.email, user_update.current_password):
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Incorrect current password"
                )
            
            # Update password
            update_data["hashed_password"] = get_password_hash(user_update.new_password)
        
        # If there are updates, apply them
        if update_data:
            for key, value in update_data.items():
                setattr(current_user, key, value)
            
            current_user.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(current_user)
        
        # Return updated user data
        return {
            "success": True,
            "message": "User updated successfully",
            "data": current_user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"Error updating user: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="An error occurred while updating the user"
        )

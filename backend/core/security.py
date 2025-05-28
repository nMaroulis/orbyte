from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import SessionLocal, get_db

# Security configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def get_user(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()

def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> models.User:
    print("\n=== get_current_user started ===")
    print(f"Token received (first 20 chars): {token[:20]}..." if token else "No token provided")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    def log_error(message: str):
        print(f"❌ ERROR: {message}")
        return credentials_exception
    
    try:
        # Ensure we have a valid token
        if not token:
            print("❌ No token provided")
            raise credentials_exception
            
        print("🔑 Token format check...")
        # Ensure the token starts with 'Bearer '
        if not token.startswith('Bearer '):
            print("ℹ️  Adding 'Bearer ' prefix to token")
            token = f'Bearer {token}'
        
        # Extract the token part after 'Bearer '
        token_parts = token.split(' ')
        if len(token_parts) > 1:
            token = token_parts[1]
            print(f"ℹ️  Extracted token (first 10 chars): {token[:10]}...")
        else:
            token = token_parts[0]
            print(f"ℹ️  Using token as-is (first 10 chars): {token[:10]}...")
        
        # Verify the token is not empty
        if not token:
            print("❌ Empty token after processing")
            raise credentials_exception
            
        print("🔍 Decoding JWT token...")
        # Decode the token
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"✅ Token decoded successfully. Payload: {payload}")
            
            email: str = payload.get("sub")
            if not email:
                print("❌ No 'sub' (email) in token payload")
                raise credentials_exception
                
            print(f"📧 Extracted email from token: {email}")
                
        except JWTError as e:
            print(f"❌ JWT Error: {e}")
            print(f"Token that caused error: {token}")
            raise credentials_exception
        
        print(f"🔍 Looking up user with email: {email}")
        # Get the user from the database
        user = get_user(db, email=email)
        if user is None:
            print(f"❌ User not found with email: {email}")
            raise credentials_exception
            
        print(f"✅ User found: ID={user.id}, Email={user.email}")
        
        # Convert SQLAlchemy model to dict for Pydantic
        user_dict = {
            "id": user.id,
            "email": user.email,
            "wallet_address": user.wallet_address,
            "is_active": user.is_active,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "updated_at": user.updated_at
        }
        
        print(f"📦 User data prepared: {user_dict}")
        
        # Create a new User instance from the dict to ensure Pydantic validation
        user_model = models.User(**user_dict)
        print("✅ User model created successfully")
        return user_model
        
    except Exception as e:
        print(f"Unexpected error in get_current_user: {e}")
        raise credentials_exception

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

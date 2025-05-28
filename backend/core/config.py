import os
from typing import List, Optional
import pydantic
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Orbyte API"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"  # Change this in production
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]  # In production, specify your frontend URL
    
    @field_validator('CORS_ORIGINS', mode='before')
    @classmethod
    def assemble_cors_origins(cls, v) -> list[str]:
        if v is None:
            return ["*"]
        if isinstance(v, str):
            if v == '*':
                return ["*"]
            if v.startswith('[') and v.endswith(']'):
                import json
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    return ["*"]
            return [v.strip() for v in v.split(',') if v.strip()]
        return v
    
    # Database
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'orbyte.db')}"
    
    # JWT
    JWT_ALGORITHM: str = "HS256"
    
    # Temporarily disable .env file loading
    model_config = {
        "case_sensitive": True,
        "env_file": None  # Disable .env file loading temporarily
    }

# Create settings instance with hardcoded values
settings = Settings(
    DEBUG=True,
    SECRET_KEY="temporary-secret-key-for-development",
    ACCESS_TOKEN_EXPIRE_MINUTES=10080,
    CORS_ORIGINS=["*"],
    DATABASE_URL=f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'orbyte.db')}",
    JWT_ALGORITHM="HS256"
)

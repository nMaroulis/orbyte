from datetime import datetime, timezone
from typing import Any, Dict, Optional
from fastapi.encoders import jsonable_encoder


def get_utc_now() -> datetime:
    """Get current UTC datetime"""
    return datetime.now(timezone.utc)


def model_to_dict(model_instance, exclude: Optional[set] = None) -> Dict[str, Any]:
    """Convert SQLAlchemy model instance to dictionary"""
    if exclude is None:
        exclude = set()
    
    result = {}
    for column in model_instance.__table__.columns:
        if column.name not in exclude:
            result[column.name] = getattr(model_instance, column.name)
    return result


def create_response(
    success: bool,
    message: str,
    data: Any = None,
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """Create a standardized API response"""
    response = {
        "success": success,
        "message": message,
    }
    
    if data is not None:
        response["data"] = jsonable_encoder(data)
    
    return response


def validate_wallet_address(address: str) -> bool:
    """Validate an Ethereum wallet address"""
    if not address.startswith("0x"):
        return False
    
    if len(address) != 42:  # 0x + 40 hex characters
        return False
    
    try:
        int(address, 16)
        return True
    except ValueError:
        return False

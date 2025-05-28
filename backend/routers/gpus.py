from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from .. import models, schemas
from ..database import get_db
from ..core.security import get_current_active_user
from ..utils.gpu_detection import get_system_gpus

# Set up logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="",
    tags=["gpus"],
    responses={404: {"description": "Not found"}},
    redirect_slashes=False  # Handle both with and without trailing slashes
)

@router.post("/", response_model=schemas.GPUResponse, status_code=status.HTTP_201_CREATED)
async def register_gpu(
    gpu: schemas.GPUCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Register a new GPU for rental
    """
    db_gpu = models.GPU(
        **gpu.dict(),
        owner_id=current_user.id,
        status=schemas.GPUStatus.AVAILABLE
    )
    
    db.add(db_gpu)
    db.commit()
    db.refresh(db_gpu)
    
    return {
        "success": True,
        "message": "GPU registered successfully",
        "data": db_gpu
    }

@router.get("", response_model=schemas.GPUsResponse)
@router.get("/", response_model=schemas.GPUsResponse)
async def list_gpus(
    skip: int = 0,
    limit: int = 100,
    min_vram: Optional[int] = None,
    max_price: Optional[float] = None,
    model: Optional[schemas.GPUModel] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all GPUs with optional filters
    """
    query = db.query(models.GPU)
    
    # Apply filters
    if min_vram is not None:
        query = query.filter(models.GPU.vram_gb >= min_vram)
    if max_price is not None:
        query = query.filter(models.GPU.price_per_hour <= max_price)
    if model is not None:
        query = query.filter(models.GPU.model == model)
    if status is not None:
        # Handle status filter
        try:
            status_enum = schemas.GPUStatus(status.lower())
            query = query.filter(models.GPU.status == status_enum)
        except ValueError:
            # If status is not valid, return empty list
            return {
                "success": True,
                "message": "Invalid status filter",
                "data": []
            }
    
    gpus = query.offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "message": f"Found {len(gpus)} GPUs",
        "data": gpus
    }

@router.get("/my-gpus", response_model=schemas.GPUsResponse)
async def list_my_gpus(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List all GPUs owned by the current user
    """
    gpus = db.query(models.GPU).filter(
        models.GPU.owner_id == current_user.id
    ).all()
    
    return {
        "success": True,
        "message": f"Found {len(gpus)} of your GPUs",
        "data": gpus
    }

@router.get("/{gpu_id}", response_model=schemas.GPUResponse)
async def get_gpu(
    gpu_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific GPU
    """
    db_gpu = db.query(models.GPU).filter(models.GPU.id == gpu_id).first()
    if not db_gpu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GPU not found"
        )
    
    return {
        "success": True,
        "message": "GPU retrieved successfully",
        "data": db_gpu
    }

@router.put("/{gpu_id}", response_model=schemas.GPUResponse)
async def update_gpu(
    gpu_id: int,
    gpu_in: schemas.GPUUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Update GPU details (only for owner)
    """
    db_gpu = db.query(models.GPU).filter(models.GPU.id == gpu_id).first()
    if not db_gpu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GPU not found"
        )
    
    if db_gpu.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update fields
    update_data = gpu_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_gpu, field, value)
    
    db_gpu.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_gpu)
    
    return {
        "success": True,
        "message": "GPU updated successfully",
        "data": db_gpu
    }

@router.delete("/{gpu_id}", response_model=schemas.GPUResponse)
async def delete_gpu(
    gpu_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Delete a GPU (only for owner)
    """
    db_gpu = db.query(models.GPU).filter(models.GPU.id == gpu_id).first()
    
    if not db_gpu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GPU not found"
        )
    
    if db_gpu.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this GPU"
        )
    
    # Check if GPU is in use
    if db_gpu.status == schemas.GPUStatus.IN_USE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete a GPU that is currently in use"
        )
    
    db.delete(db_gpu)
    db.commit()
    
    return {
        "success": True,
        "message": "GPU deleted successfully",
        "data": db_gpu
    }

@router.get("/system-gpus", response_model=Dict[str, Any])
async def list_system_gpus(
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List all NVIDIA GPUs available on the system
    """
    try:
        gpus = get_system_gpus()
        return {
            "success": True,
            "message": f"Found {len(gpus)} system GPUs",
            "data": gpus
        }
    except RuntimeError as e:
        logger.error(f"Error getting system GPUs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system GPUs: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting system GPUs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while getting system GPUs"
        )

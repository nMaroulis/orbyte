from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import logging

from .. import models
from ..schemas import (
    GPUDetailResponse, GPUStatus, GPUResponse, GPUsResponse, 
    GPU, GPUCreate, GPUUpdate
)
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

@router.post("/", response_model=GPUResponse, status_code=status.HTTP_201_CREATED)
async def register_gpu(
    gpu: GPUCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Register a new GPU for rental
    """
    db_gpu = models.GPU(
        **gpu.dict(),
        owner_id=current_user.id,
        status=GPUStatus.AVAILABLE
    )
    
    db.add(db_gpu)
    db.commit()
    db.refresh(db_gpu)
    
    return {
        "success": True,
        "message": "GPU registered successfully",
        "data": db_gpu
    }

@router.get("", response_model=GPUsResponse)
@router.get("/", response_model=GPUsResponse)
async def list_gpus(
    skip: int = 0,
    limit: int = 100,
    min_vram: Optional[int] = None,
    max_price: Optional[float] = None,
    model: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all GPUs with optional filters
    """
    query = db.query(models.GPU)
    
    # Apply filters
    if min_vram is not None and min_vram > 0:
        query = query.filter(models.GPU.vram_gb >= min_vram)
    if max_price is not None and max_price > 0:
        query = query.filter(models.GPU.price_per_hour <= max_price)
    if model is not None and model.strip() != "":
        query = query.filter(models.GPU.model.ilike(f"%{model}%"))
    if status is not None and status.strip() != "":
        # Handle status filter
        try:
            status_enum = GPUStatus(status.lower())
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

@router.get("/my-gpus", response_model=GPUsResponse)
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

@router.get("/{gpu_id}/details", response_model=GPUDetailResponse)
async def get_gpu_details(
    gpu_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get detailed information about a specific GPU including workflows and models
    """
    # Get the GPU with relationships loaded
    gpu = db.query(models.GPU).filter(models.GPU.id == gpu_id).first()
    
    if not gpu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"GPU with ID {gpu_id} not found"
        )
    
    # Check if user is owner or admin (for future reference in the response)
    is_owner = gpu.owner_id == current_user.id
    is_admin = current_user.is_admin
    can_edit = is_owner or is_admin
    
    # Get workflows for this GPU
    workflows = db.query(models.GPUWorkflow).filter(
        models.GPUWorkflow.gpu_id == gpu_id
    ).all()
    
    # Get models for this GPU
    gpu_models = db.query(models.LLMModel).filter(
        models.LLMModel.gpu_id == gpu_id
    ).all()
    
    # Convert SQLAlchemy objects to dictionaries
    gpu_data = {
        "id": gpu.id,
        "name": gpu.name,
        "model": gpu.model,
        "vram_gb": gpu.vram_gb,
        "price_per_hour": gpu.price_per_hour,
        "status": gpu.status.value,
        "os": gpu.os,
        "cpu_model": gpu.cpu_model,
        "cpu_cores": gpu.cpu_cores,
        "ram_gb": gpu.ram_gb,
        "storage_gb": gpu.storage_gb,
        "network_speed_mbps": gpu.network_speed_mbps,
        "specs": gpu.specs or {},
        "created_at": gpu.created_at,
        "updated_at": gpu.updated_at
    }
    
    workflows_data = [
        {
            "id": wf.id,
            "workflow_type": wf.workflow_type.value,
            "status": wf.status.value,
            "config": wf.config or {},
            "created_at": wf.created_at,
            "updated_at": wf.updated_at
        }
        for wf in workflows
    ]
    
    models_data = [
        {
            "id": model.id,
            "model_type": model.model_type,
            "model_name": model.model_name,
            "model_path": model.model_path,
            "is_active": model.is_active,
            "created_at": model.created_at,
            "updated_at": model.updated_at
        }
        for model in gpu_models
    ]
    
    return {
        "success": True,
        "message": "GPU details retrieved successfully",
        "data": {
            "gpu": gpu_data,
            "workflows": workflows_data,
            "models": models_data,
            "permissions": {
                "can_edit": can_edit,
                "is_owner": is_owner,
                "is_admin": is_admin
            }
        }
    }

@router.get("/{gpu_id}", response_model=GPUResponse)
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

@router.put("/{gpu_id}", response_model=GPUResponse)
async def update_gpu(
    gpu_id: int,
    gpu_in: GPUUpdate,
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

@router.delete("/{gpu_id}", response_model=GPUResponse)
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
    if db_gpu.status == GPUStatus.IN_USE:
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
    
    This endpoint returns a list of NVIDIA GPUs detected on the system
    with their details including name, memory, and other specifications.
    """
    try:
        gpus = get_system_gpus()
        return {
            "success": True,
            "message": f"Found {len(gpus)} GPUs",
            "data": gpus
        }
    except Exception as e:
        logger.error(f"Error getting system GPUs: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting system GPUs: {str(e)}"
        )

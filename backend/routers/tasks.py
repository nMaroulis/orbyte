from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid
import time

from .. import models, schemas
from ..database import get_db
from ..core.security import get_current_active_user
from ..services.task_processor import process_task

router = APIRouter(
    prefix="",
    tags=["tasks"],
    responses={404: {"description": "Not found"}},
    redirect_slashes=False  # Handle both with and without trailing slashes
)

@router.post("/", response_model=schemas.TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task: schemas.TaskCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Submit a new task for processing on the network
    """
    # Find an available GPU if not specified
    gpu = None
    if task.gpu_id:
        gpu = db.query(models.GPU).filter(
            models.GPU.id == task.gpu_id,
            models.GPU.status == schemas.GPUStatus.AVAILABLE
        ).first()
    else:
        # Find the first available GPU that meets the requirements
        gpu = db.query(models.GPU).filter(
            models.GPU.status == schemas.GPUStatus.AVAILABLE
        ).first()
    
    if not gpu:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No available GPUs found to process this task"
        )
    
    # Create the task
    db_task = models.Task(
        **task.dict(exclude={"gpu_id"}),
        requester_id=current_user.id,
        gpu_id=gpu.id,
        status=schemas.TaskStatus.PENDING
    )
    
    # Mark GPU as in use
    gpu.status = schemas.GPUStatus.IN_USE
    
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Start processing the task in the background
    background_tasks.add_task(process_task, db=db, task_id=db_task.id)
    
    return {
        "success": True,
        "message": "Task submitted successfully",
        "data": db_task
    }

@router.get("", response_model=schemas.TasksResponse)
@router.get("/", response_model=schemas.TasksResponse)
@router.get("/api/tasks", response_model=schemas.TasksResponse)
@router.get("/api/tasks/", response_model=schemas.TasksResponse)
async def list_tasks(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    task_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List all tasks for the current user with optional filters
    """
    query = db.query(models.Task).filter(
        (models.Task.requester_id == current_user.id) |
        (models.Task.gpu.has(owner_id=current_user.id))
    )
    

    # Apply status filter if provided
    if status is not None:
        try:
            status_enum = schemas.TaskStatus(status.lower())
            query = query.filter(models.Task.status == status_enum)
        except ValueError:
            # If status is not valid, return empty list
            return {
                "success": True,
                "message": "Invalid status filter",
                "data": []
            }
    
    # Apply task type filter if provided
    if task_type is not None:
        try:
            task_type_enum = schemas.TaskType(task_type.lower())
            query = query.filter(models.Task.task_type == task_type_enum)
        except ValueError:
            # If task type is not valid, return empty list
            return {
                "success": True,
                "message": "Invalid task type filter",
                "data": []
            }
    
    tasks = query.order_by(models.Task.created_at.desc())\
                 .offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "message": f"Found {len(tasks)} tasks",
        "data": tasks
    }

@router.get("/{task_id}", response_model=schemas.TaskResponse)
async def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get details of a specific task
    """
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.requester_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )
    
    return {
        "success": True,
        "message": "Task retrieved successfully",
        "data": db_task
    }

@router.post("/{task_id}/cancel", response_model=schemas.TaskResponse)
async def cancel_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Cancel a pending or running task
    """
    db_task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.requester_id == current_user.id
    ).first()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )
    
    if db_task.status not in [schemas.TaskStatus.PENDING, schemas.TaskStatus.RUNNING]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel task with status {db_task.status}"
        )
    
    # Update task status
    db_task.status = schemas.TaskStatus.CANCELLED
    db_task.updated_at = datetime.utcnow()
    
    # Mark GPU as available again
    if db_task.gpu:
        db_task.gpu.status = schemas.GPUStatus.AVAILABLE
    
    db.commit()
    db.refresh(db_task)
    
    return {
        "success": True,
        "message": "Task cancelled successfully",
        "data": db_task
    }

@router.get("/gpu/{gpu_id}", response_model=schemas.TasksResponse)
async def get_gpu_tasks(
    gpu_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all tasks for a specific GPU (only for GPU owner)
    """
    # Verify the GPU belongs to the current user
    gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not gpu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GPU not found or access denied"
        )
    
    tasks = db.query(models.Task).filter(
        models.Task.gpu_id == gpu_id
    ).order_by(models.Task.created_at.desc()).all()
    
    return {
        "success": True,
        "message": f"Found {len(tasks)} tasks for GPU {gpu_id}",
        "data": tasks
    }

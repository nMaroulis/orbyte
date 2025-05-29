from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from .. import models
from ..models.gpu_workflow import GPUWorkflow, WorkflowType, WorkflowStatus
from ..models.gpu_model import GPUModel
from ..schemas.workflow import (
    GPUWorkflowCreate, GPUWorkflowResponse, GPUWorkflowsResponse,
    GPUModelCreate, GPUModelResponse, GPUModelsResponse, GPUWorkflowConfig
)
from ..database import get_db
from ..core.security import get_current_active_user

router = APIRouter(
    prefix="",
    tags=["workflows"],
    responses={404: {"description": "Not found"}},
)

# Workflow endpoints
@router.post("/workflows", response_model=GPUWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def add_workflow_to_gpu(
    gpu_id: int,
    workflow: GPUWorkflowCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Add a supported workflow to a GPU
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    # Check if workflow already exists
    existing = db.query(GPUWorkflow).filter(
        GPUWorkflow.gpu_id == gpu_id,
        GPUWorkflow.workflow_type == workflow.workflow_type
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Workflow already exists for this GPU")
    
    # Create new workflow
    db_workflow = GPUWorkflow(
        gpu_id=gpu_id,
        workflow_type=workflow.workflow_type,
        status=workflow.status if hasattr(workflow, 'status') else WorkflowStatus.PENDING,
        config=workflow.config if hasattr(workflow, 'config') else {}
    )
    
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    
    return {"success": True, "message": "Workflow added successfully", "data": db_workflow}

@router.get("/workflows", response_model=GPUWorkflowsResponse)
async def get_gpu_workflows(
    gpu_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all workflows for a specific GPU
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    workflows = db.query(GPUWorkflow).filter(GPUWorkflow.gpu_id == gpu_id).all()
    return {"success": True, "message": f"Found {len(workflows)} workflows", "data": workflows}

@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_workflow_from_gpu(
    gpu_id: int,
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Remove a workflow from a GPU
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    # Find and delete the workflow
    workflow = db.query(GPUWorkflow).filter(
        GPUWorkflow.id == workflow_id,
        GPUWorkflow.gpu_id == gpu_id
    ).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    
    return {"success": True, "message": "Workflow removed successfully"}

# Model endpoints
@router.post("/models", response_model=GPUModelResponse, status_code=status.HTTP_201_CREATED)
async def add_model_to_gpu(
    gpu_id: int,
    model: GPUModelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Add an installed model to a GPU
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    # Check if model already exists
    existing = db.query(GPUModel).filter(
        GPUModel.gpu_id == gpu_id,
        GPUModel.model_name == model.model_name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Model with this name already exists for this GPU")
    
    # Create new model
    db_model = GPUModel(
        gpu_id=gpu_id,
        model_name=model.model_name,
        model_type=model.model_type,
        model_path=model.model_path if hasattr(model, 'model_path') else None,
        model_config=model.model_config if hasattr(model, 'model_config') else {}
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return {"success": True, "message": "Model added successfully", "data": db_model}

@router.get("/models", response_model=GPUModelsResponse)
async def get_gpu_models(
    gpu_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all installed models for a specific GPU
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    models = db.query(GPUModel).filter(GPUModel.gpu_id == gpu_id).all()
    return {"success": True, "message": f"Found {len(models)} models", "data": models}

@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_model_from_gpu(
    gpu_id: int,
    model_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Remove a model from a GPU
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    # Find and delete the model
    model = db.query(GPUModel).filter(
        GPUModel.id == model_id,
        GPUModel.gpu_id == gpu_id
    ).first()
    
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db.delete(model)
    db.commit()
    
    return {"success": True, "message": "Model removed successfully"}

@router.post("/configure-workflows", response_model=dict)
async def configure_gpu_workflows(
    gpu_id: int,
    config: GPUWorkflowConfig,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Configure workflows and models for a GPU in a single request
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    # Start a transaction
    try:
        # Clear existing workflows and models
        db.query(GPUWorkflow).filter(GPUWorkflow.gpu_id == gpu_id).delete()
        db.query(GPUModel).filter(GPUModel.gpu_id == gpu_id).delete()
        
        # Add new workflows
        for workflow in config.workflows:
            db_workflow = GPUWorkflow(
                gpu_id=gpu_id,
                workflow_type=workflow.workflow_type,
                status=workflow.status if hasattr(workflow, 'status') else WorkflowStatus.PENDING,
                config=workflow.config if hasattr(workflow, 'config') else {}
            )
            db.add(db_workflow)
        
        # Add new models
        for model in config.installed_models:
            db_model = GPUModel(
                gpu_id=gpu_id,
                model_name=model.model_name,
                model_type=model.model_type,
                model_path=model.model_path if hasattr(model, 'model_path') else None,
                model_config=model.model_config if hasattr(model, 'model_config') else {}
            )
            db.add(db_model)
        
        db.commit()
        
        # Get updated lists
        workflows = db.query(GPUWorkflow).filter(GPUWorkflow.gpu_id == gpu_id).all()
        models = db.query(GPUModel).filter(GPUModel.gpu_id == gpu_id).all()
        
        return {
            "success": True,
            "message": "GPU configuration updated successfully",
            "data": {
                "workflows": workflows,
                "installed_models": models
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

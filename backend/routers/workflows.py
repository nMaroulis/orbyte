from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from .. import models
from ..models.gpu_workflow import GPUWorkflow, WorkflowType, WorkflowStatus
from ..models.llm_model import LLMModel, LLMModelType
from ..schemas.workflow import (
    GPUWorkflowCreate, GPUWorkflowResponse, GPUWorkflowsResponse, GPUWorkflowConfig
)
from ..schemas.llm_model import (
    LLMModelCreate, LLMModelResponse, LLMModelsResponse, LLMModelUpdate
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
@router.post("/models", response_model=LLMModelResponse, status_code=status.HTTP_201_CREATED)
async def add_model_to_gpu(
    gpu_id: int,
    model: LLMModelCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Add an installed LLM model to a GPU
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    # Check if model already exists
    existing = db.query(LLMModel).filter(
        LLMModel.gpu_id == gpu_id,
        LLMModel.model_name == model.model_name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Model with this name already exists for this GPU"
        )
    
    # Create new model
    db_model = LLMModel(
        gpu_id=gpu_id,
        model_type=model.model_type,
        model_name=model.model_name,
        model_path=model.model_path,
        is_active=model.is_active
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return {
        "success": True, 
        "message": "LLM model added to GPU", 
        "data": db_model
    }

@router.get("/models", response_model=LLMModelsResponse)
async def get_gpu_models(
    gpu_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get all installed LLM models for a specific GPU
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(status_code=404, detail="GPU not found")
    
    models = db.query(LLMModel).filter(LLMModel.gpu_id == gpu_id).all()
    return {
        "success": True, 
        "message": f"Found {len(models)} LLM models", 
        "data": models
    }

@router.delete("/models/{model_id}", status_code=status.HTTP_200_OK)
async def remove_model_from_gpu(
    gpu_id: int,
    model_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Remove an LLM model from a GPU
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="GPU not found"
        )
    
    # Verify model exists and belongs to the current user
    db_model = db.query(LLMModel).join(
        models.GPU, LLMModel.gpu_id == models.GPU.id
    ).filter(
        LLMModel.id == model_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LLM model not found"
        )
    
    # Delete the model
    db.delete(db_model)
    db.commit()
    
    return {
        "success": True, 
        "message": "LLM model removed from GPU"
    }

@router.post("/configure-workflows", response_model=dict)
async def configure_gpu_workflows(
    gpu_id: int,
    config: GPUWorkflowConfig,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Configure workflows and LLM models for a GPU in a single request
    """
    # Verify GPU exists and belongs to the current user
    db_gpu = db.query(models.GPU).filter(
        models.GPU.id == gpu_id,
        models.GPU.owner_id == current_user.id
    ).first()
    
    if not db_gpu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="GPU not found"
        )
    
    # Start a transaction
    try:
        # Clear existing workflows and models
        db.query(GPUWorkflow).filter(GPUWorkflow.gpu_id == gpu_id).delete()
        db.query(LLMModel).filter(LLMModel.gpu_id == gpu_id).delete()
        
        # Add new workflows
        for workflow in config.supported_workflows:
            db_workflow = GPUWorkflow(
                gpu_id=gpu_id,
                workflow_type=workflow,
                status=WorkflowStatus.PENDING,
                config={}
            )
            db.add(db_workflow)
        
        # Add new models
        for model_data in config.installed_models:
            db_model = LLMModel(
                gpu_id=gpu_id,
                model_name=model_data.get('model_name', 'Unnamed Model'),
                model_type=model_data.get('model_type', LLMModelType.GPT_3_5_TURBO),
                model_path=model_data.get('model_path'),
                is_active=model_data.get('is_active', True)
            )
            db.add(db_model)
        
        db.commit()
        
        # Get updated lists
        workflows = db.query(GPUWorkflow).filter(GPUWorkflow.gpu_id == gpu_id).all()
        models = db.query(LLMModel).filter(LLMModel.gpu_id == gpu_id).all()
        
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update GPU configuration: {str(e)}"
        )

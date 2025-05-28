from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import uuid

from .. import models, schemas
from ..database import get_db
from ..core.security import get_current_active_user

router = APIRouter(
    prefix="",
    tags=["payments"],
    responses={404: {"description": "Not found"}},
    redirect_slashes=False  # Handle both with and without trailing slashes
)

@router.get("/", response_model=schemas.PaymentsResponse)
async def list_payments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[schemas.PaymentStatus] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List all payments for the current user (both sent and received)
    """
    query = db.query(models.Payment).filter(
        (models.Payment.payer_id == current_user.id) | 
        (models.Payment.recipient_id == current_user.id)
    )
    
    if status:
        query = query.filter(models.Payment.status == status)
    
    payments = query.order_by(models.Payment.created_at.desc())\
                    .offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "message": f"Found {len(payments)} payments",
        "data": payments
    }

@router.get("/sent", response_model=schemas.PaymentsResponse)
async def list_sent_payments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[schemas.PaymentStatus] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List all payments sent by the current user
    """
    query = db.query(models.Payment).filter(
        models.Payment.payer_id == current_user.id
    )
    
    if status:
        query = query.filter(models.Payment.status == status)
    
    payments = query.order_by(models.Payment.created_at.desc())\
                    .offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "message": f"Found {len(payments)} sent payments",
        "data": payments
    }

@router.get("/received", response_model=schemas.PaymentsResponse)
@router.get("/received/", response_model=schemas.PaymentsResponse)
@router.get("/api/payments/received", response_model=schemas.PaymentsResponse)
@router.get("/api/payments/received/", response_model=schemas.PaymentsResponse)
async def list_received_payments(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    List all payments received by the current user
    """
    query = db.query(models.Payment)

    
    # Apply status filter if provided
    if status is not None:
        try:
            status_enum = schemas.PaymentStatus(status.lower())
            query = query.filter(models.Payment.status == status_enum)
        except ValueError:
            # If status is not valid, return empty list
            return {
                "success": True,
                "message": "Invalid status filter",
                "data": []
            }
    
    payments = query.order_by(models.Payment.created_at.desc())\
                    .offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "message": f"Found {len(payments)} received payments",
        "data": payments
    }


@router.get("/{payment_id}", response_model=schemas.PaymentResponse)
async def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Get details of a specific payment
    """
    payment = db.query(models.Payment).filter(
        models.Payment.id == payment_id,
        ((models.Payment.payer_id == current_user.id) | 
         (models.Payment.recipient_id == current_user.id))
    ).first()
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found or access denied"
        )
    
    return {
        "success": True,
        "message": "Payment retrieved successfully",
        "data": payment
    }

@router.post("/{task_id}/pay", response_model=schemas.PaymentResponse)
async def create_payment(
    task_id: int,
    payment_in: schemas.PaymentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a payment for a completed task
    """
    # Get the task
    task = db.query(models.Task).filter(
        models.Task.id == task_id,
        models.Task.requester_id == current_user.id,
        models.Task.status == schemas.TaskStatus.COMPLETED
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found, not completed, or access denied"
        )
    
    # Check if payment already exists for this task
    existing_payment = db.query(models.Payment).filter(
        models.Payment.task_id == task_id
    ).first()
    
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment already exists for this task"
        )
    
    # Validate payment amount (should match task cost)
    if payment_in.amount != task.cost:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount must be equal to task cost: {task.cost}"
        )
    
    # Create payment
    db_payment = models.Payment(
        **payment_in.dict(),
        task_id=task_id,
        payer_id=current_user.id,
        recipient_id=task.gpu.owner_id,
        status=schemas.PaymentStatus.PENDING,
        transaction_hash=f"0x{uuid.uuid4().hex}"  # Mock transaction hash
    )
    
    # In a real implementation, we would interact with a blockchain here
    # For now, we'll just mark the payment as completed
    db_payment.status = schemas.PaymentStatus.COMPLETED
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    
    return {
        "success": True,
        "message": "Payment created and processed successfully",
        "data": db_payment
    }

import time
import random
from datetime import datetime
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal

def process_task(db: Session, task_id: int):
    """
    Process a task in the background
    """
    try:
        # Create a new session for this background task
        db = SessionLocal()
        
        # Get the task
        task = db.query(models.Task).filter(
            models.Task.id == task_id
        ).first()
        
        if not task:
            print(f"Task {task_id} not found")
            return
        
        # Update task status to running
        task.status = schemas.TaskStatus.RUNNING
        task.started_at = datetime.utcnow()
        db.commit()
        
        # Simulate processing time (1-5 seconds)
        processing_time = random.uniform(1, 5)
        time.sleep(processing_time)
        
        # Simulate task success/failure (80% success rate)
        if random.random() < 0.8:  # 80% success rate
            # Task completed successfully
            task.status = schemas.TaskStatus.COMPLETED
            task.output_data = {
                "result": "Task completed successfully",
                "processing_time_seconds": round(processing_time, 2),
                "mock_data": {
                    "generated_text": "This is a mock response from the AI model. In a real implementation, this would be the actual model output.",
                    "tokens_generated": random.randint(10, 100),
                    "inference_time": round(processing_time, 2)
                }
            }
            # Calculate cost based on processing time and GPU rate
            task.cost = round(task.gpu.price_per_hour * (processing_time / 3600), 6)
        else:
            # Task failed
            task.status = schemas.TaskStatus.FAILED
            task.output_data = {
                "error": "Task processing failed",
                "reason": "Simulated random failure"
            }
        
        # Mark GPU as available again
        if task.gpu:
            task.gpu.status = schemas.GPUStatus.AVAILABLE
        
        task.completed_at = datetime.utcnow()
        db.commit()
        
        print(f"Task {task_id} processed with status: {task.status}")
        
    except Exception as e:
        print(f"Error processing task {task_id}: {str(e)}")
        # Try to update task status to failed
        try:
            task = db.query(models.Task).filter(
                models.Task.id == task_id
            ).first()
            if task:
                task.status = schemas.TaskStatus.FAILED
                task.output_data = {
                    "error": "Internal server error",
                    "details": str(e)
                }
                if task.gpu:
                    task.gpu.status = schemas.GPUStatus.AVAILABLE
                db.commit()
        except:
            pass
    finally:
        db.close()

def process_payment(db: Session, payment_id: int):
    """
    Process a payment in the background
    In a real implementation, this would interact with a blockchain
    """
    try:
        # Get the payment
        payment = db.query(models.Payment).filter(
            models.Payment.id == payment_id
        ).first()
        
        if not payment:
            print(f"Payment {payment_id} not found")
            return
        
        # In a real implementation, I should:
        # 1. Verify the transaction on the blockchain
        # 2. Update the payment status based on the transaction status
        # 3. Handle any errors or retries
        
        # For now, I'll just simulate a successful payment after a short delay
        time.sleep(2)
        
        payment.status = schemas.PaymentStatus.COMPLETED
        db.commit()
        
        print(f"Payment {payment_id} processed successfully")
        
    except Exception as e:
        print(f"Error processing payment {payment_id}: {str(e)}")
        # Try to update payment status to failed
        try:
            payment = db.query(models.Payment).filter(
                models.Payment.id == payment_id
            ).first()
            if payment:
                payment.status = schemas.PaymentStatus.FAILED
                db.commit()
        except:
            pass
    finally:
        db.close()

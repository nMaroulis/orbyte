import sys
import os
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database and models first to ensure proper registration
from backend.database import engine, Base, SessionLocal
from backend.core.security import get_password_hash
from backend.schemas.llm_model import LLMModelType

# Import all models to ensure they are registered with SQLAlchemy
from backend.models.user import User  # noqa: F401
from backend.models.gpu import GPU, GPUStatus  # noqa: F401
from backend.models.llm_model import LLMModel  # noqa: F401
from backend.models.gpu_workflow import GPUWorkflow  # noqa: F401
from backend.models.task import Task  # noqa: F401
from backend.models.payment import Payment  # noqa: F401

# Import the models module to ensure all models are registered
from backend import models  # noqa: F401

def init_db():
    """Initialize the database with required tables and initial data"""
    print("Creating database tables...")
    
    # First create all tables
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        print(f"Database URL: {engine.url}")
        print(f"Tables in metadata: {Base.metadata.tables.keys()}")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Now create a session for adding data
    db = SessionLocal()
    try:
        # Verify the connection by querying the database using 2.0 style
        from sqlalchemy import text
        db.execute(text('SELECT 1'))
        db.commit()
        print("✅ Database connection verified")
        # Create initial admin user if not exists
        admin_email = "admin@orbyte.com"
        demo_email = "demo@orbyte.com"
        
        # Check and create admin user
        admin_user = db.query(User).filter(
            User.email == admin_email
        ).first()
        
        if not admin_user:
            print("Creating admin user...")
            admin_user = User(
                email=admin_email,
                wallet_address="0x0000000000000000000000000000000000000000",
                hashed_password=get_password_hash("admin123"),
                is_active=True,
                is_admin=True
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            print(f"✅ Created admin user with email: {admin_email}")
            print(f"   Default password: admin123")
            print(f"   Please change this password after first login!")
        else:
            print(f"ℹ️  Admin user already exists: {admin_email}")
            
        # Create demo user if not exists
        demo_user = db.query(User).filter(
            User.email == demo_email
        ).first()
        
        if not demo_user:
            print("Creating demo user...")
            demo_user = User(
                email=demo_email,
                wallet_address="0x1111111111111111111111111111111111111111",
                hashed_password=get_password_hash("demopassword123"),
                is_active=True,
                is_admin=False
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print(f"✅ Created demo user with email: {demo_email}")
            print(f"   Demo password: demopassword123")
        else:
            print(f"ℹ️  Demo user already exists: {demo_email}")
        
        # Create some sample GPUs if none exist
        gpu_count = db.query(models.GPU).count()
        if gpu_count == 0:
            print("Creating sample GPUs...")
            sample_gpus = [
                models.GPU(
                    name="RTX 4090 - High Performance",
                    model="NVIDIA GeForce RTX 4090",
                    vram_gb=24,
                    price_per_hour=0.5,
                    status=GPUStatus.AVAILABLE,
                    owner_id=admin_user.id,
                    specs={
                        "cuda_cores": 16384,
                        "base_clock": 2235,
                        "boost_clock": 2520,
                        "memory_type": "GDDR6X",
                        "memory_bus": 384,
                        "bandwidth": 1008,
                        "supported_models": ["GPT-4", "Llama 3 70B", "Mistral 7B"]
                    }
                ),
                models.GPU(
                    name="A100 - AI Workstation",
                    model="NVIDIA A100 80GB",
                    vram_gb=80,
                    price_per_hour=1.5,
                    status=GPUStatus.AVAILABLE,
                    owner_id=admin_user.id,
                    specs={
                        "cuda_cores": 6912,
                        "tensor_cores": 432,
                        "memory_type": "HBM2",
                        "memory_bus": 5120,
                        "bandwidth": 1555,
                        "supported_models": ["Llama 3 70B", "Mistral 7B", "CodeLlama 34B"]
                    },
                    os="Ubuntu 22.04 LTS",
                    cpu_model="AMD Ryzen Threadripper 3990X",
                    cpu_cores=64,
                    ram_gb=512,
                    storage_gb=4000,
                    network_speed_mbps=1000
                ),
                models.GPU(
                    name="H100 - Next Gen AI",
                    model="NVIDIA H100 80GB",
                    vram_gb=80,
                    price_per_hour=2.0,
                    status=GPUStatus.AVAILABLE,
                    owner_id=admin_user.id,
                    specs={
                        "cuda_cores": 16896,
                        "tensor_cores": 528,
                        "memory_type": "HBM3",
                        "memory_bus": 5120,
                        "bandwidth": 3000,
                        "supported_models": ["GPT-4", "Llama 3 70B", "Mistral 7B", "CodeLlama 34B", "Llama 2 70B"]
                    },
                    os="Ubuntu 20.04 LTS",
                    cpu_model="AMD EPYC 7763",
                    cpu_cores=128,
                    ram_gb=1024,
                    storage_gb=8000,
                    network_speed_mbps=10000
                )
            ]
            
            db.add_all(sample_gpus)
            db.commit()
            print(f"✅ Created {len(sample_gpus)} sample GPUs")
            
            # Create some sample LLM models for the GPUs
            print("Creating sample LLM models...")
            sample_models = []
            for gpu in sample_gpus:
                sample_models.extend([
                    LLMModel(
                        gpu_id=gpu.id,
                        model_type=LLMModelType.GPT_4_TURBO,
                        model_name="GPT-4 Turbo",
                        model_path="/models/gpt-4-turbo",
                        is_active=True
                    ),
                    LLMModel(
                        gpu_id=gpu.id,
                        model_type=LLMModelType.LLAMA_3_70B,
                        model_name="Llama 3 70B",
                        model_path="/models/llama-3-70b",
                        is_active=True
                    )
                ])
            
            db.add_all(sample_models)
            db.commit()
            print(f"✅ Created {len(sample_models)} sample LLM models")
        else:
            print(f"ℹ️  Found {gpu_count} existing GPUs")
        
        db.close()
        print("✅ Database initialized successfully!")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Database error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        db.rollback()
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db.close()
        except:
            pass
    
    return True

if __name__ == "__main__":
    print("🚀 Initializing Orbyte Database...")
    success = init_db()
    if not success:
        print("❌ Failed to initialize database")
        sys.exit(1)

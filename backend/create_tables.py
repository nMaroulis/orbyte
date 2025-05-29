import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import Base, engine
from models.gpu import GPU, GPUStatus, GPUModel as GPUModelEnum
from models.workflow import GPUWorkflow, GPUModel

# Create all tables
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database tables created successfully!")

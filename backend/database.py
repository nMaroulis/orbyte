from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from .core.config import settings

# Create SQLAlchemy engine
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=True
)

# Create a custom session class that filters out unexpected kwargs
class CustomSession(Session):
    def __init__(self, **kwargs):
        # Only pass through known session arguments
        allowed_kwargs = {
            'bind', 'binds', 'autoflush', 'autocommit',
            'expire_on_commit', 'info', 'twophase', 'weak_identity_map'
        }
        filtered_kwargs = {k: v for k, v in kwargs.items() if k in allowed_kwargs}
        super().__init__(**filtered_kwargs)

# Create session factory with our custom session class
SessionLocal = sessionmaker(
    class_=CustomSession,
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class
Base = declarative_base()

def get_db():
    """
    Dependency function that yields db sessions
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

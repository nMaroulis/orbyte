# Import all models to ensure they are registered with SQLAlchemy
from .models import User, GPU, Task, Payment  # noqa: F401

# This makes the models available when importing from the package
__all__ = [
    'User',
    'GPU',
    'Task',
    'Payment',
]

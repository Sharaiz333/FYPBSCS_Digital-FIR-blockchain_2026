# Import every SQLModel table class here so SQLModel.metadata.create_all
# (called in core/database.py) knows about it. This is the one place a
# new model file must be registered.
from app.models.user import User  # noqa: F401
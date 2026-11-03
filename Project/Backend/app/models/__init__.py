# Register all SQLModel table classes for Alembic.
from app.models.user import User  # noqa: F401
# Import every SQLModel table class here so SQLModel.metadata (used by
# Alembic and by the tests) knows about it. A new model file MUST be
# registered here, otherwise Alembic will not see its table.
from app.models.user import User  # noqa: F401
from app.models.station import PoliceStation  # noqa: F401
from app.models.complaint import Complaint  # noqa: F401
from app.models.fir import FIR  # noqa: F401
from app.models.audit import AuditLog  # noqa: F401
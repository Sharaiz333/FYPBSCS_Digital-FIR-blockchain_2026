import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from sqlmodel import Session, select
from app.core.database import engine, init_db
from app.core.security import hash_password
from app.models.enums import RoleName
from app.models.user import User

# Development-only demo accounts with synthetic data.
DEMO_USERS = [
    ("System Admin", "admin", "AdminPass123", RoleName.ADMIN),
    ("Supervisory Officer", "supervisor1", "Pass1234", RoleName.SUPERVISORY_OFFICER),
    ("Investigating Officer", "io1", "Pass1234", RoleName.INVESTIGATING_OFFICER),
    ("Front Desk Officer", "officer1", "Pass1234", RoleName.POLICE_OFFICER),
    ("Audit Review Officer", "auditor1", "Pass1234", RoleName.AUDIT_REVIEW_OFFICER),
    ("Demo Citizen", "citizen1", "Pass1234", RoleName.CITIZEN),
]

init_db()
with Session(engine) as session:
    for full_name, username, password, role in DEMO_USERS:
        if session.exec(select(User).where(User.username == username)).first():
            print(f"skip {username}")
            continue
        session.add(User(full_name=full_name, username=username,
                         password_hash=hash_password(password), role=role))
        print(f"created {username} ({role.value})")
    session.commit()
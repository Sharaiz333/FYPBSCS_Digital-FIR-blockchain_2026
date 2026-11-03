r"""
Seed demo stations and demo accounts (synthetic, development only).

Run from the backend/ folder with the virtual environment active, AFTER
the tables exist (alembic upgrade head):

    cd backend
    python ..\database\seed\seed.py          (Windows)
    python ../database/seed/seed.py          (macOS / Linux)

Safe to run more than once: anything that already exists is skipped.
Never use these credentials anywhere real.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "backend"))

from sqlalchemy import inspect  # noqa: E402
from sqlmodel import Session, select  # noqa: E402

from app.core.database import engine  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.enums import RoleName  # noqa: E402
from app.models.station import PoliceStation  # noqa: E402
from app.models.user import User  # noqa: E402

DEMO_STATIONS = [
    ("Saddar Police Station", "Rawalpindi"),
    ("Abbottabad City Police Station", "Abbottabad"),
    ("Blue Area Police Station", "Islamabad"),
]

DEMO_USERS = [
    ("System Admin", "admin", "AdminPass123", RoleName.ADMIN),
    ("Supervisory Officer", "supervisor1", "Pass1234", RoleName.SUPERVISORY_OFFICER),
    ("Front Desk Officer", "officer1", "Pass1234", RoleName.POLICE_OFFICER),
    ("Investigating Officer One", "io1", "Pass1234", RoleName.INVESTIGATING_OFFICER),
    ("Investigating Officer Two", "io2", "Pass1234", RoleName.INVESTIGATING_OFFICER),
    ("Audit Review Officer", "auditor1", "Pass1234", RoleName.AUDIT_REVIEW_OFFICER),
    ("Demo Citizen One", "citizen1", "Pass1234", RoleName.CITIZEN),
    ("Demo Citizen Two", "citizen2", "Pass1234", RoleName.CITIZEN),
]


def main() -> None:
    if not inspect(engine).has_table("users"):
        print("The database tables do not exist yet. Run:  alembic upgrade head   (from backend/) and try again.")
        sys.exit(1)

    with Session(engine) as session:
        for name, location in DEMO_STATIONS:
            if session.exec(select(PoliceStation).where(PoliceStation.name == name)).first():
                print(f"skip station  {name}")
                continue
            session.add(PoliceStation(name=name, location=location))
            print(f"created station  {name}")

        for full_name, username, password, role in DEMO_USERS:
            if session.exec(select(User).where(User.username == username)).first():
                print(f"skip user     {username}")
                continue
            session.add(User(full_name=full_name, username=username,
                             password_hash=hash_password(password), role=role))
            print(f"created user  {username:12} {role.value}")
        session.commit()


if __name__ == "__main__":
    main()
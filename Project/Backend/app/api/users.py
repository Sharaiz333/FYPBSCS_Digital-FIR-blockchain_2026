from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.deps import get_current_user, require_role
from app.core.security import hash_password
from app.models.enums import RoleName
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

# NOTE: "/me" is declared before "/{user_id}" so FastAPI doesn't treat
# the word "me" as a user id.


@router.get("/me", response_model=UserRead)
def read_my_profile(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(
    payload: UserCreate,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_role(RoleName.ADMIN)),
):
    if session.exec(select(User).where(User.username == payload.username)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    if payload.email and session.exec(select(User).where(User.email == payload.email)).first():
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already in use")

    user = User(
        full_name=payload.full_name,
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@router.get("", response_model=list[UserRead])
def list_users(
    role: RoleName | None = None,
    is_active: bool | None = None,
    session: Session = Depends(get_session),
    _admin: User = Depends(require_role(RoleName.ADMIN)),
):
    statement = select(User)
    if role is not None:
        statement = statement.where(User.role == role)
    if is_active is not None:
        statement = statement.where(User.is_active == is_active)
    return session.exec(statement.order_by(User.created_at)).all()


@router.patch("/{user_id}", response_model=UserRead)
def update_user(
    user_id: str,
    payload: UserUpdate,
    session: Session = Depends(get_session),
    admin: User = Depends(require_role(RoleName.ADMIN)),
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")

    changes = payload.model_dump(exclude_unset=True)

    # Lock-out protection: an admin must not be able to remove their own access.
    if user.user_id == admin.user_id:
        if changes.get("is_active") is False:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot deactivate your own account")
        if "role" in changes and changes["role"] != admin.role:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "You cannot change your own role")

    new_email = changes.get("email")
    if new_email and new_email != user.email:
        if session.exec(select(User).where(User.email == new_email)).first():
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already in use")

    for field, value in changes.items():
        setattr(user, field, value)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user
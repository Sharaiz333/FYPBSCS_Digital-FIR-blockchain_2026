from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import create_access_token, verify_password
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == payload.username)).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        # Same error for "no such user" and "wrong password" - don't leak which usernames exist.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    return TokenResponse(
        access_token=create_access_token(user.user_id, user.role.value),
        role=user.role,
        user_id=user.user_id,
        full_name=user.full_name,
    )
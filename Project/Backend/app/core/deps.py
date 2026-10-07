from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session

from app.core.database import get_session
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    error = HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise error
    user = session.get(User, payload.get("sub"))
    if not user or not user.is_active:
        raise error
    return user
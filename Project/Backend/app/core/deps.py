from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session
from app.models.enums import RoleName

from app.core.database import get_session
from app.core.security import decode_token
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def require_role(*allowed_roles: RoleName):
    """Usage: current_user: User = Depends(require_role(RoleName.ADMIN))"""

    def _checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            # Generic message on purpose: don't reveal which roles ARE allowed.
            raise HTTPException(status.HTTP_403_FORBIDDEN, "You do not have permission to perform this action")
        return current_user

    return _checker


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    error = HTTPException(status.HTTP_401_UNAUTHORIZED, "Could not validate credentials")
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise error
    user = session.get(User, payload.get("sub"))
    if not user or not user.is_active:
        raise error
    return user
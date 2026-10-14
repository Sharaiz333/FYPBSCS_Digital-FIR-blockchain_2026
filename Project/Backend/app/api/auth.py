from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import create_access_token, hash_password, verify_password
from app.models.enums import RoleName, VerificationStatus
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, RegisterResponse, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == payload.username)).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        # Same error for "no such user" and "wrong password" - don't leak which usernames exist.
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")

    # Only reached with a CORRECT password, so these messages don't help
    # someone who is just guessing usernames.
    if user.verification_status == VerificationStatus.PENDING:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Your account is awaiting verification by a police officer.")
    if user.verification_status == VerificationStatus.REJECTED:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "Your registration was not approved. Please visit your police station with your original CNIC.",
        )

    return TokenResponse(
        access_token=create_access_token(user.user_id, user.role.value),
        role=user.role,
        user_id=user.user_id,
        full_name=user.full_name,
    )


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register_citizen(payload: RegisterRequest, session: Session = Depends(get_session)):
    """Public. Creates a citizen account that CANNOT log in until an officer verifies it."""
    existing_cnic = session.exec(select(User).where(User.cnic == payload.cnic)).first()

    # A previously REJECTED citizen may re-apply: we reuse their old (never-usable)
    # record. Any other existing record with this CNIC is a duplicate.
    reapplying = existing_cnic is not None and existing_cnic.verification_status == VerificationStatus.REJECTED
    if existing_cnic is not None and not reapplying:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with these details already exists")

    same_username = session.exec(select(User).where(User.username == payload.username)).first()
    if same_username is not None and same_username is not existing_cnic:
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already exists")
    if payload.email:
        same_email = session.exec(select(User).where(User.email == payload.email)).first()
        if same_email is not None and same_email is not existing_cnic:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already in use")

    user = existing_cnic if reapplying else User(role=RoleName.CITIZEN, password_hash="")
    user.full_name = payload.full_name
    user.username = payload.username
    user.email = payload.email
    user.password_hash = hash_password(payload.password)
    user.cnic = payload.cnic
    user.phone = payload.phone
    user.address = payload.address
    user.verification_status = VerificationStatus.PENDING
    user.verified_by = None
    user.verified_at = None
    user.rejection_reason = None
    session.add(user)
    session.commit()

    return RegisterResponse(
        message="Registration received. A police officer must verify your identity before you can log in.",
        verification_status=VerificationStatus.PENDING,
    )
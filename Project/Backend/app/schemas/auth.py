from pydantic import BaseModel, EmailStr, Field

from app.models.enums import RoleName, VerificationStatus


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleName
    user_id: str
    full_name: str


class RegisterRequest(BaseModel):
    """Public citizen registration. There is deliberately NO role field:
    anyone registering here is a citizen, and nothing the client sends can change that."""

    full_name: str = Field(min_length=2, max_length=100)
    username: str = Field(min_length=3, max_length=50, pattern=r"^[A-Za-z0-9_.-]+$")
    email: EmailStr | None = None
    password: str = Field(min_length=8, max_length=128)
    cnic: str = Field(pattern=r"^\d{5}-\d{7}-\d$")
    phone: str = Field(pattern=r"^03\d{2}-?\d{7}$")
    address: str | None = Field(default=None, max_length=200)


class RegisterResponse(BaseModel):
    message: str
    verification_status: VerificationStatus
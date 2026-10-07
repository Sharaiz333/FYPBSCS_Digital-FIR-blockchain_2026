from pydantic import BaseModel
from app.models.enums import RoleName


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: RoleName
    user_id: str
    full_name: str
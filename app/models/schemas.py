from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import UserRole

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    name: str
    password: str
    role: UserRole = UserRole.REGULAR

class UserResponse(BaseModel):
    id: int
    email: str
    name: str
    role: UserRole
    is_active: bool
    created_at: datetime
    version: int

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    version: int
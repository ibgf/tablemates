from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = "新用户"
    avatar: Optional[str] = None


class UserLogin(BaseModel):
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

class LoginRequest(BaseModel):
    email_or_phone: str
    password: str    

class UserOut(BaseModel):
    id: UUID
    phone: Optional[str]
    email: Optional[EmailStr]
    full_name: str
    avatar: Optional[str]
    created_at: datetime
    is_verified: bool
    role: str

    model_config = ConfigDict(from_attributes=True)


class AuthBinding(BaseModel):
    provider: str
    provider_user_id: str

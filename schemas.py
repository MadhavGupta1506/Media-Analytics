"""
Pydantic Models (Schemas)
"""
from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: int
    email: EmailStr

class SignupIn(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_rules(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class MediaOut(BaseModel):
    id: int
    title: str
    type: str
    file_url: str
    created_at: datetime

    class Config:
        from_attributes = True

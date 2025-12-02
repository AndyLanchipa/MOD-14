import re
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        # Enforce length with custom messages to satisfy tests
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters long")
        if len(v) > 50:
            raise ValueError("Username must be less than 50 characters long")
        # Only allow letters, numbers, and underscores
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username can only contain letters, numbers, and underscores"
            )
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        # Enforce minimum length with custom message
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        # Check byte length for bcrypt compatibility (bcrypt has 72-byte limit)
        if len(v.encode("utf-8")) > 72:
            raise ValueError(
                "Password cannot exceed 72 UTF-8 bytes (bcrypt limit). "
                "Use fewer characters or avoid special Unicode characters."
            )
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    created_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

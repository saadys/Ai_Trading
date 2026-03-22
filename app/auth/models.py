import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class Base(DeclarativeBase):
    pass

class RoleEnum(str, Enum):
    ADMIN = "admin"
    TRADER = "trader"
    VIEWER = "viewer"

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    role = Column(String(20), default=RoleEnum.VIEWER, nullable=False)
    two_fa_secret = Column(String(64), nullable=True)
    two_fa_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    refresh_token = Column(Text, unique=True, nullable=False, index=True)
    is_valid = Column(Boolean, default=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    revoked_at = Column(DateTime, nullable=True)
    user = relationship("User", back_populates="sessions")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    two_fa_code: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int
    two_fa_required: bool = False

class UserResponse(BaseModel):
    id: str
    email: str
    is_verified: bool
    two_fa_enabled: bool
    role: str
    created_at: datetime
    class Config:
        from_attributes = True

class TwoFASetupResponse(BaseModel):
    qr_code_uri: str
    secret: str

class TwoFAVerifyRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)

class MessageResponse(BaseModel):
    message: str
    success: bool = True
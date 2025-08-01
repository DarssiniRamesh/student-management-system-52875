"""
Admin-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator


class AdminBase(BaseModel):
    """Base admin schema with common fields."""
    username: str = Field(..., min_length=3, max_length=100, description="Unique admin username")
    email: EmailStr = Field(..., description="Admin's email address")
    full_name: str = Field(..., min_length=1, max_length=200, description="Admin's full name")
    is_superuser: bool = Field(False, description="Whether admin has superuser privileges")
    is_admin: bool = Field(True, description="Whether user has admin privileges")
    permissions: Dict[str, Any] = Field(default_factory=dict, description="Specific permissions")
    notes: Optional[str] = Field(None, description="Additional notes about the admin")


class AdminCreate(AdminBase):
    """Schema for creating a new admin."""
    password: str = Field(..., min_length=8, description="Admin password (minimum 8 characters)")

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')  
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class AdminUpdate(BaseModel):
    """Schema for updating admin information."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    is_superuser: Optional[bool] = None
    is_admin: Optional[bool] = None
    permissions: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, description="New password (optional)")

    @validator('password')
    def validate_password(cls, v):
        if v is not None:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            if not any(c.isupper() for c in v):
                raise ValueError('Password must contain at least one uppercase letter')
            if not any(c.islower() for c in v):
                raise ValueError('Password must contain at least one lowercase letter')  
            if not any(c.isdigit() for c in v):
                raise ValueError('Password must contain at least one digit')
        return v


class AdminResponse(AdminBase):
    """Schema for admin response (excludes sensitive information)."""
    id: int = Field(..., description="Internal database ID")
    created_at: datetime = Field(..., description="When the admin record was created")
    updated_at: datetime = Field(..., description="When the admin record was last updated")
    is_active: bool = Field(..., description="Whether the admin record is active")

    class Config:
        from_attributes = True


class AdminLogin(BaseModel):
    """Schema for admin login."""
    username: str = Field(..., description="Admin username or email")
    password: str = Field(..., description="Admin password")


class AdminToken(BaseModel):
    """Schema for admin authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    admin: AdminResponse = Field(..., description="Admin information")

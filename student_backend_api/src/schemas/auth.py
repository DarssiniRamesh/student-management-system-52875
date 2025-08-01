"""
Authentication-related Pydantic schemas for request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

from .admin import AdminResponse


class LoginRequest(BaseModel):
    """Schema for authentication login request."""
    username: str = Field(..., description="Username or email address", min_length=1)
    password: str = Field(..., description="User password", min_length=1)


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    user: AdminResponse = Field(..., description="Authenticated user information")


class TokenData(BaseModel):
    """Schema for token payload data."""
    user_id: Optional[str] = Field(None, description="User ID from token")
    username: Optional[str] = Field(None, description="Username from token")
    expires: Optional[datetime] = Field(None, description="Token expiration time")


class RefreshTokenRequest(BaseModel):
    """Schema for token refresh request."""
    refresh_token: str = Field(..., description="Refresh token")


class ChangePasswordRequest(BaseModel):
    """Schema for password change request."""
    current_password: str = Field(..., description="Current password", min_length=1)
    new_password: str = Field(..., description="New password", min_length=8)
    confirm_password: str = Field(..., description="Confirm new password", min_length=8)


class ResetPasswordRequest(BaseModel):
    """Schema for password reset request."""
    email: str = Field(..., description="User email address")


class ResetPasswordConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str = Field(..., description="Password reset token")
    new_password: str = Field(..., description="New password", min_length=8)
    confirm_password: str = Field(..., description="Confirm new password", min_length=8)


class AuthStatus(BaseModel):
    """Schema for authentication status response."""
    authenticated: bool = Field(..., description="Whether user is authenticated")
    user: Optional[AdminResponse] = Field(None, description="User information if authenticated")
    permissions: Optional[dict] = Field(None, description="User permissions if authenticated")

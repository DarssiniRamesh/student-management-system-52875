"""
Authentication and authorization related Pydantic schemas for request/response validation.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr, Extra

# PUBLIC_INTERFACE
class LoginRequest(BaseModel):
    """
    Schema for login requests (username/email and password).
    """
    username: str = Field(..., description="Username or email address")
    password: str = Field(..., description="User password")

# PUBLIC_INTERFACE
class TokenResponse(BaseModel):
    """
    Response schema for successful login or token refresh.
    """
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")

# PUBLIC_INTERFACE
class TokenData(BaseModel):
    """
    Data stored within JWT tokens.
    """
    sub: Optional[str] = Field(None, description="Subject (user id)")
    role: Optional[str] = Field(None, description="Role (admin or user)")
    exp: Optional[int] = Field(None, description="Expiration timestamp")

# PUBLIC_INTERFACE
class ChangePasswordRequest(BaseModel):
    """
    Schema for change password requests.
    """
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., description="New password (minimum 8 characters)")

# PUBLIC_INTERFACE
class AuthStatus(BaseModel):
    """
    Schema indicating current authentication status.
    """
    is_authenticated: bool = Field(..., description="Is user authenticated")
    username: Optional[str] = Field(None, description="Username if authenticated")
    role: Optional[str] = Field(None, description="User role")

# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT Token model (alias for compatibility, used by routers)."""
    access_token: str
    token_type: str

# PUBLIC_INTERFACE
class UserInDB(BaseModel):
    """Internal user representation"""
    id: int
    email: EmailStr
    hashed_password: str
    role: str

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """User login payload (alias for compatibility)"""
    username: EmailStr
    password: str

# PUBLIC_INTERFACE
class RegisterRequest(BaseModel):
    """
    Registration request schema for user or admin.
    Only these fields are accepted: type, username, email, full_name, password, is_superuser, is_admin, permissions, notes.
    Any unknown field will be rejected with a 422 error.
    """
    type: str = Field("user", description="Account type: 'user' or 'admin'")
    username: str = Field(..., min_length=3, max_length=100, description="Username for the new account")
    email: EmailStr = Field(..., description="Email address for the new account")
    full_name: str = Field(..., min_length=1, max_length=200, description="Full name of the new account holder")
    password: str = Field(..., min_length=8, description="Password for the account (minimum 8 chars)")
    # Admin fields (optional for users)
    is_superuser: Optional[bool] = False
    is_admin: Optional[bool] = True
    permissions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    notes: Optional[str] = None

    class Config:
        extra = Extra.forbid
        schema_extra = {
            "example": {
                "type": "user",
                "username": "testuser",
                "email": "testuser@example.com",
                "full_name": "Test User",
                "password": "ValidPass1"
            }
        }

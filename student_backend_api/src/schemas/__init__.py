"""
Pydantic schemas package for request/response validation.
"""
from .student import StudentCreate, StudentUpdate, StudentResponse, StudentList
from .admin import AdminCreate, AdminUpdate, AdminResponse, AdminLogin
from .auth import LoginRequest, TokenResponse, TokenData, ChangePasswordRequest, AuthStatus
from .common import BaseResponse, PaginatedResponse

__all__ = [
    "StudentCreate", "StudentUpdate", "StudentResponse", "StudentList",
    "AdminCreate", "AdminUpdate", "AdminResponse", "AdminLogin",
    "LoginRequest", "TokenResponse", "TokenData", "ChangePasswordRequest", "AuthStatus",
    "BaseResponse", "PaginatedResponse"
]

"""
Pydantic schemas package for request/response validation.
"""
from .student import StudentCreate, StudentUpdate, StudentResponse, StudentList
from .admin import AdminCreate, AdminUpdate, AdminResponse, AdminLogin
from .auth import (
    LoginRequest,
    TokenResponse,
    TokenData,
    ChangePasswordRequest,
    AuthStatus,
    Token,
    UserInDB,
    UserLogin,
)
from .common import BaseResponse, PaginatedResponse
from .config import (
    ConfigCreate, ConfigUpdate, ConfigResponse,
    FeatureToggleCreate, FeatureToggleUpdate, FeatureToggleResponse,
    RuntimeConfigResponse, ConfigBulkUpdate, ConfigExportResponse, ConfigImportRequest
)

__all__ = [
    "StudentCreate", "StudentUpdate", "StudentResponse", "StudentList",
    "AdminCreate", "AdminUpdate", "AdminResponse", "AdminLogin",
    "LoginRequest", "TokenResponse", "TokenData", "ChangePasswordRequest", "AuthStatus",
    "Token", "UserInDB", "UserLogin",
    "BaseResponse", "PaginatedResponse",
    "ConfigCreate", "ConfigUpdate", "ConfigResponse",
    "FeatureToggleCreate", "FeatureToggleUpdate", "FeatureToggleResponse",
    "RuntimeConfigResponse", "ConfigBulkUpdate", "ConfigExportResponse", "ConfigImportRequest"
]

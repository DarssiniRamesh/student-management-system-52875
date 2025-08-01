"""
Pydantic schemas package for request/response validation.
"""
from .student import StudentCreate, StudentUpdate, StudentResponse, StudentList
from .admin import AdminCreate, AdminUpdate, AdminResponse, AdminLogin
from .common import BaseResponse, PaginatedResponse

__all__ = [
    "StudentCreate", "StudentUpdate", "StudentResponse", "StudentList",
    "AdminCreate", "AdminUpdate", "AdminResponse", "AdminLogin",
    "BaseResponse", "PaginatedResponse"
]

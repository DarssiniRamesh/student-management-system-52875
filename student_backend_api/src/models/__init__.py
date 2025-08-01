"""
Database models package.
"""
from .base import Base
from .student import Student
from .admin import Admin

__all__ = ["Base", "Student", "Admin"]

"""
Student-related Pydantic schemas for request/response validation.
"""
from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator

from .common import PaginatedResponse


class StudentBase(BaseModel):
    """Base student schema with common fields."""
    student_id: str = Field(..., min_length=1, max_length=50, description="Unique student identifier")
    first_name: str = Field(..., min_length=1, max_length=100, description="Student's first name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Student's last name")
    email: EmailStr = Field(..., description="Student's email address")
    phone: Optional[str] = Field(None, max_length=20, description="Student's phone number")
    date_of_birth: Optional[date] = Field(None, description="Student's date of birth")
    address: Optional[str] = Field(None, description="Student's address")
    enrollment_status: Optional[str] = Field("active", max_length=50, description="Current enrollment status")
    grade_level: Optional[str] = Field(None, max_length=20, description="Current grade or class level")
    notes: Optional[str] = Field(None, description="Additional notes about the student")

    @validator('enrollment_status')
    def validate_enrollment_status(cls, v):
        allowed_statuses = ['active', 'inactive', 'graduated', 'transferred', 'suspended']
        if v and v not in allowed_statuses:
            raise ValueError(f'Enrollment status must be one of: {", ".join(allowed_statuses)}')
        return v


class StudentCreate(StudentBase):
    """Schema for creating a new student."""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating student information."""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    date_of_birth: Optional[date] = None
    address: Optional[str] = None
    enrollment_status: Optional[str] = Field(None, max_length=50)
    grade_level: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None

    @validator('enrollment_status')
    def validate_enrollment_status(cls, v):
        if v is not None:
            allowed_statuses = ['active', 'inactive', 'graduated', 'transferred', 'suspended']
            if v not in allowed_statuses:
                raise ValueError(f'Enrollment status must be one of: {", ".join(allowed_statuses)}')
        return v


class StudentResponse(StudentBase):
    """Schema for student response with additional metadata."""
    id: int = Field(..., description="Internal database ID")
    created_at: datetime = Field(..., description="When the student record was created")
    updated_at: datetime = Field(..., description="When the student record was last updated")
    is_active: bool = Field(..., description="Whether the student record is active")
    full_name: str = Field(..., description="Student's full name")

    class Config:
        from_attributes = True


class StudentList(PaginatedResponse[StudentResponse]):
    """Paginated list of students."""
    pass

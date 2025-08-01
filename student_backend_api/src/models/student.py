"""
Student model definition.
"""
from sqlalchemy import Column, String, Date, Text

from .base import BaseModel


class Student(BaseModel):
    """
    Student model for managing student data in the system.
    
    Attributes:
        student_id: Unique student identifier
        first_name: Student's first name
        last_name: Student's last name
        email: Student's email address
        phone: Student's phone number
        date_of_birth: Student's date of birth
        address: Student's address
        enrollment_status: Current enrollment status
        grade_level: Current grade or class level
        notes: Additional notes about the student
    """
    __tablename__ = "students"

    student_id = Column(String(50), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20))
    date_of_birth = Column(Date)
    address = Column(Text)
    enrollment_status = Column(String(50), default="active")
    grade_level = Column(String(20))
    notes = Column(Text)

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, student_id={self.student_id}, name={self.first_name} {self.last_name})>"

    @property
    def full_name(self) -> str:
        """Return full name of the student."""
        return f"{self.first_name} {self.last_name}"

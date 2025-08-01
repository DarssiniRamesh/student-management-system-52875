"""
Admin model definition.
"""
from sqlalchemy import Column, String, Boolean, Text, JSON
from passlib.context import CryptContext

from .base import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Admin(BaseModel):
    """
    Admin model for managing administrative users and their permissions.
    
    Attributes:
        username: Unique admin username
        email: Admin's email address
        full_name: Admin's full name
        hashed_password: Securely hashed admin password
        is_superuser: Whether admin has superuser privileges
        is_admin: Whether user has admin privileges
        permissions: JSON field storing specific permissions
        last_login: Timestamp of last login
        notes: Additional notes about the admin
    """
    __tablename__ = "admins"

    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_superuser = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=True)
    permissions = Column(JSON, default=dict)
    notes = Column(Text)

    def verify_password(self, plain_password: str) -> bool:
        """Verify a plain password against the hashed password."""
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a plain password."""
        return pwd_context.hash(password)
    
    def set_password(self, password: str) -> None:
        """Set the admin's password (hashed)."""
        self.hashed_password = self.hash_password(password)

    def __repr__(self) -> str:
        return f"<Admin(id={self.id}, username={self.username}, email={self.email})>"

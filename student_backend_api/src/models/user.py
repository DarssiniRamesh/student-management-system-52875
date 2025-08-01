"""
User model definition for student portal users.
"""
from sqlalchemy import Column, String, Boolean, JSON, DateTime
from passlib.context import CryptContext

from .base import BaseModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    """
    User model for student portal users (different from admin users).
    
    This model represents regular users who access the student portal,
    as opposed to admin users who access the admin portal.
    
    Attributes:
        username: Unique username for login
        email: User's email address
        full_name: User's full name
        hashed_password: Securely hashed user password
        is_verified: Whether user's email is verified
        is_student: Whether user is a student
        profile_data: JSON field for additional profile information
        last_login: Timestamp of last login
        failed_login_attempts: Number of consecutive failed login attempts
        locked_until: Timestamp until which account is locked (if applicable)
    """
    __tablename__ = "users"

    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(200), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_student = Column(Boolean, default=True)
    profile_data = Column(JSON, default=dict)
    last_login = Column(DateTime(timezone=True))
    failed_login_attempts = Column(String(10), default="0")
    locked_until = Column(DateTime(timezone=True))

    def verify_password(self, plain_password: str) -> bool:
        """
        Verify a plain password against the hashed password.
        
        Args:
            plain_password: The plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, self.hashed_password)
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a plain password.
        
        Args:
            password: The plain text password to hash
            
        Returns:
            str: The hashed password
        """
        return pwd_context.hash(password)
    
    def set_password(self, password: str) -> None:
        """
        Set the user's password (hashed).
        
        Args:
            password: The plain text password to set
        """
        self.hashed_password = self.hash_password(password)

    def increment_failed_attempts(self) -> None:
        """Increment failed login attempts counter."""
        try:
            current_attempts = int(self.failed_login_attempts or "0")
            self.failed_login_attempts = str(current_attempts + 1)
        except (ValueError, TypeError):
            self.failed_login_attempts = "1"

    def reset_failed_attempts(self) -> None:
        """Reset failed login attempts counter."""
        self.failed_login_attempts = "0"
        self.locked_until = None

    def is_locked(self) -> bool:
        """
        Check if user account is locked.
        
        Returns:
            bool: True if account is locked, False otherwise
        """
        if self.locked_until is None:
            return False
        
        from datetime import datetime
        return datetime.utcnow() < self.locked_until

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

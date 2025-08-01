"""
JWT authentication and authorization utilities for FastAPI.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from .database import get_db
from .security import verify_token
from ..models.admin import Admin

security = HTTPBearer()

# PUBLIC_INTERFACE
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Admin:
    """
    Dependency to get the current authenticated admin user.
    
    Args:
        credentials: HTTP authorization credentials with Bearer token
        db: Database session
        
    Returns:
        Admin: The authenticated admin user
        
    Raises:
        HTTPException: If authentication fails
    """
    token = credentials.credentials
    
    try:
        payload = verify_token(token)
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    admin = db.query(Admin).filter(Admin.id == int(user_id)).first()
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return admin

# PUBLIC_INTERFACE
def get_current_active_user(
    current_user: Admin = Depends(get_current_user)
) -> Admin:
    """
    Dependency to get the current authenticated and active admin user.
    
    Args:
        current_user: The current authenticated user
        
    Returns:
        Admin: The authenticated and active admin user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# PUBLIC_INTERFACE  
def get_current_superuser(
    current_user: Admin = Depends(get_current_active_user)
) -> Admin:
    """
    Dependency to get the current authenticated superuser.
    
    Args:
        current_user: The current authenticated and active user
        
    Returns:
        Admin: The authenticated superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# PUBLIC_INTERFACE
def optional_auth(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[Admin]:
    """
    Optional authentication dependency that allows both authenticated and anonymous access.
    
    Args:
        credentials: Optional HTTP authorization credentials
        db: Database session
        
    Returns:
        Optional[Admin]: The authenticated admin user or None for anonymous access
    """
    if credentials is None:
        return None
    
    try:
        return get_current_user(credentials, db)
    except HTTPException:
        return None

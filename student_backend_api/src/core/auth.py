from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from src.core.security import decode_access_token
from src.core.database import get_db
from src.models.admin import Admin
from src.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Retrieve authenticated user or raise"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str = payload.get("sub")
        role = payload.get("role")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if role == "admin":
        user = db.query(Admin).filter(Admin.id == int(user_id)).first()
    else:
        user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user

# PUBLIC_INTERFACE
def get_current_active_admin(current_user = Depends(get_current_user)):
    """Ensure current user is admin."""
    # If using SQLAlchemy inheritance, type check may suffice.
    if not hasattr(current_user, "is_superuser") and not hasattr(current_user, "role"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: admin required",
        )
    # Accepts is_superuser True OR role == admin
    if (getattr(current_user, "is_superuser", False) is not True
        and getattr(current_user, "role", None) != "admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: admin required",
        )
    return current_user

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.schemas.auth import Token
from src.models.admin import Admin
from src.models.user import User
from src.core.security import create_access_token, verify_password

# PUBLIC_INTERFACE
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)

ACCESS_TOKEN_EXPIRE_MINUTES = 60

# PUBLIC_INTERFACE
@router.post("/login", summary="Login for access token", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user or admin and return a JWT token if successful.

    - **username**: str, as username or email
    - **password**: str, plain text password
    Returns:
        - **access_token**: JWT string
        - **token_type**: "bearer"
    """
    user = (
        db.query(Admin).filter(Admin.email == form_data.username).first()
        or db.query(User).filter(User.email == form_data.username).first()
    )

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_dict = {
        "sub": str(user.id),
        "role": "admin" if isinstance(user, Admin) else "user",
    }
    access_token = create_access_token(
        data=user_dict,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}

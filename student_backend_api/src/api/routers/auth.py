from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any

from src.core.database import get_db
from src.schemas.auth import Token, UserLogin
from src.schemas.admin import AdminCreate
from src.schemas.common import BaseResponse
from src.models.admin import Admin
from src.models.user import User
from src.core.security import create_access_token, verify_password, get_password_hash

# Pydantic schema for registration request
class RegisterRequest(BaseModel):
    """
    Registration request schema for user or admin.
    """
    type: str = Field("user", description="Account type: 'user' or 'admin'")
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr = Field(...)
    full_name: str = Field(..., min_length=1, max_length=200)
    password: str = Field(..., min_length=8)
    # Admin fields
    is_superuser: Optional[bool] = False
    is_admin: Optional[bool] = True
    permissions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    notes: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "type": "user",
                "username": "testuser",
                "email": "testuser@example.com",
                "full_name": "Test User",
                "password": "ValidPass1"
            }
        }

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

# PUBLIC_INTERFACE
@router.post(
    "/register",
    summary="Register new user or admin",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    description="Register a new user or admin. Prevents duplicate usernames/emails. Passwords are securely hashed.",
    responses={
        201: {"description": "Registration successful"},
        400: {"description": "User or admin with given email/username already exists"},
    },
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user or admin.

    Provide fields:
        - type: "admin" or "user"
        - username
        - email
        - full_name
        - password
        [for admin: is_superuser, is_admin, permissions, notes (optional)]
    Returns success or error.
    """
    user_type = payload.type
    username = payload.username
    email = payload.email
    full_name = payload.full_name
    password = payload.password

    # Duplicate check: username/email across both admin/user
    admin_exists = db.query(Admin).filter(
        (Admin.username == username) | (Admin.email == email)
    ).first()
    user_exists = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if admin_exists or user_exists:
        raise HTTPException(status_code=400, detail="A user or admin with that username or email already exists.")

    hashed = get_password_hash(password)
    if user_type == "admin":
        # Validate admin fields using AdminCreate
        validated = AdminCreate(
            username=username,
            email=email,
            full_name=full_name,
            is_superuser=payload.is_superuser,
            is_admin=payload.is_admin,
            permissions=payload.permissions,
            notes=payload.notes,
            password=password,
        )
        admin = Admin(
            username=validated.username,
            email=validated.email,
            full_name=validated.full_name,
            hashed_password=hashed,
            is_superuser=validated.is_superuser,
            is_admin=validated.is_admin,
            permissions=validated.permissions,
            notes=validated.notes,
        )
        db.add(admin)
    elif user_type == "user":
        # Validate user fields using UserLogin for password constraints
        _ = UserLogin(
            username=email,
            password=password,
        )
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed,
            is_verified=False,
            is_student=True,
        )
        db.add(user)
    else:
        raise HTTPException(status_code=400, detail="Invalid type, must be 'user' or 'admin'.")
    db.commit()
    return BaseResponse(
        success=True,
        message=f"{user_type.capitalize()} registered successfully."
    )

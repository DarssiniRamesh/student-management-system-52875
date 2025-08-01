from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from sqlalchemy.orm import Session


from src.core.database import get_db
from src.schemas.auth import Token, UserLogin, RegisterRequest

from src.schemas.common import BaseResponse
from src.models.admin import Admin
from src.models.user import User
from src.core.security import create_access_token, verify_password, get_password_hash

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
    summary="Register new user",
    response_model=BaseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    description="Register a new user (not admin). Prevents duplicate usernames/emails. Passwords are securely hashed.",
    responses={
        201: {"description": "Registration successful"},
        400: {"description": "User with given email/username already exists"},
        422: {"description": "Validation Error for extra or missing fields (handled by FastAPI/Pydantic, never returns 500 for unexpected fields)"}
    },
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    PUBLIC_INTERFACE
    Register a new user.

    FastAPI will always reject any request with extra or unknown fields not defined in RegisterRequest schema by returning a 422 response with standard validation error details (never a 500 error).
    This guarantees strict schema compliance for registration payloads.

    Provide fields:
        - username
        - email
        - full_name
        - password
    Returns success or error; extra root properties are disallowed and return a 422.
    """
    username = request.username
    email = request.email
    full_name = request.full_name
    password = request.password

    # Duplicate check: username/email across both admin/user
    admin_exists = db.query(Admin).filter(
        (Admin.username == username) | (Admin.email == email)
    ).first()
    user_exists = db.query(User).filter(
        (User.username == username) | (User.email == email)
    ).first()
    if admin_exists or user_exists:
        raise HTTPException(status_code=400, detail="A user with that username or email already exists.")

    hashed = get_password_hash(password)
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
    db.commit()
    return BaseResponse(
        success=True,
        message="User registered successfully."
    )

from pydantic import BaseModel, EmailStr

# PUBLIC_INTERFACE
class Token(BaseModel):
    """JWT Token model"""
    access_token: str
    token_type: str

# PUBLIC_INTERFACE
class TokenData(BaseModel):
    """Token Data extracted from JWT"""
    sub: str = None
    role: str = None

# PUBLIC_INTERFACE
class UserInDB(BaseModel):
    """Internal user representation"""
    id: int
    email: EmailStr
    hashed_password: str
    role: str

# PUBLIC_INTERFACE
class UserLogin(BaseModel):
    """User login payload"""
    username: EmailStr
    password: str

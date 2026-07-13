from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserSignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: str = Field(..., min_length=1, description="Full name is required")

class UserSignUpResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    role: str
    message: str

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserProfile(BaseModel):
    id: str
    email: str
    full_name: str
    role: str

class UserLoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserProfile

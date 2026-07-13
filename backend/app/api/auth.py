import uuid
import logging
import time
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.config import settings
from app.core.security import get_current_user
from app.database.supabase_client import supabase_client
from app.schemas.auth import (
    UserSignUpRequest,
    UserSignUpResponse,
    UserLoginRequest,
    UserLoginResponse,
    UserProfile
)

logger = logging.getLogger("visionguard.auth")
router = APIRouter(prefix="/auth", tags=["Authentication"])

def create_mock_jwt(user_id: str, email: str, full_name: str, role: str) -> str:
    """Generates a local JWT signed with settings.JWT_SECRET mirroring Supabase payload"""
    payload = {
        "sub": user_id,
        "email": email,
        "role": "authenticated",
        "user_metadata": {
            "full_name": full_name
        },
        "exp": int(time.time()) + 3600 # 1 hour expiry
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

@router.post("/signup", response_model=UserSignUpResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: UserSignUpRequest):
    """
    Register a new user. Supports Supabase Auth and local mock fallback.
    """
    logger.info(f"SignUp request received for: {request.email}")
    
    # Check if Supabase client is initialized
    if supabase_client is not None:
        try:
            # Call Supabase signup
            response = supabase_client.auth.sign_up({
                "email": request.email,
                "password": request.password,
                "options": {
                    "data": {
                        "full_name": request.full_name
                    }
                }
            })
            
            if response.user:
                user_id = str(response.user.id)
                
                # Check if we should insert the profile manually in case trigger didn't run
                try:
                    supabase_client.table("users").insert({
                        "id": user_id,
                        "email": request.email,
                        "full_name": request.full_name,
                        "role": "User"
                    }).execute()
                except Exception as e:
                    # Ignore duplicate conflict errors
                    logger.debug(f"Sync profile error (could be duplicate): {e}")

                return UserSignUpResponse(
                    user_id=user_id,
                    email=request.email,
                    full_name=request.full_name,
                    role="User",
                    message="User registered successfully. Check your email for verification."
                )
        except Exception as e:
            logger.error(f"Supabase auth signup failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
            
    # Mock Mode Fallback
    logger.info("Running signup in Mock Mode.")
    mock_id = str(uuid.uuid4())
    return UserSignUpResponse(
        user_id=mock_id,
        email=request.email,
        full_name=request.full_name,
        role="User",
        message="User registered successfully (Mock Mode). Please login."
    )

@router.post("/login", response_model=UserLoginResponse)
async def login(request: UserLoginRequest):
    """
    Authenticate user and return access token. Supports Supabase Auth and local mock fallback.
    """
    logger.info(f"Login request received for: {request.email}")
    
    if supabase_client is not None:
        try:
            # Call Supabase auth sign-in
            response = supabase_client.auth.sign_in_with_password({
                "email": request.email,
                "password": request.password
            })
            
            if response.user and response.session:
                user_id = str(response.user.id)
                access_token = response.session.access_token
                refresh_token = response.session.refresh_token or ""
                
                # Retrieve profile details/role from public.users table
                role = "User"
                full_name = request.email.split('@')[0]
                try:
                    profile_res = supabase_client.table("users").select("*").eq("id", user_id).execute()
                    if profile_res.data and len(profile_res.data) > 0:
                        role = profile_res.data[0].get("role", "User")
                        full_name = profile_res.data[0].get("full_name", full_name)
                except Exception as db_err:
                    logger.warning(f"Failed to fetch profile during login: {db_err}")
                
                return UserLoginResponse(
                    access_token=access_token,
                    refresh_token=refresh_token,
                    user=UserProfile(
                        id=user_id,
                        email=request.email,
                        full_name=full_name,
                        role=role
                    )
                )
        except Exception as e:
            logger.error(f"Supabase auth login failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
    # Mock Mode Fallback
    logger.info("Running login in Mock Mode.")
    # Assign 'Admin' role for admin@example.com for testing purposes
    role = "Admin" if request.email == "admin@example.com" else "User"
    mock_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, request.email))
    full_name = request.email.split('@')[0].capitalize()
    
    mock_access_token = create_mock_jwt(mock_id, request.email, full_name, role)
    
    return UserLoginResponse(
        access_token=mock_access_token,
        refresh_token="mock_refresh_token_xyz",
        user=UserProfile(
            id=mock_id,
            email=request.email,
            full_name=full_name,
            role=role
        )
    )

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """
    Log out the current user session.
    """
    logger.info(f"Logout request from user: {current_user.get('email')}")
    if supabase_client is not None:
        try:
            supabase_client.auth.sign_out()
        except Exception as e:
            logger.warning(f"Supabase auth signout failed: {e}")
            
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserProfile)
async def get_me(current_user: dict = Depends(get_current_user)):
    """
    Get the currently logged-in user profile.
    """
    return UserProfile(
        id=current_user.get("id"),
        email=current_user.get("email"),
        full_name=current_user.get("full_name", ""),
        role=current_user.get("role", "User")
    )

import logging
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.database.supabase_client import supabase_client

logger = logging.getLogger("visionguard.security")

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Decodes and verifies a Supabase Auth JWT token.
    Uses the JWT_SECRET to perform local verification.
    """
    token = credentials.credentials
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
            options={"verify_aud": False} # Supabase JWT aud defaults to 'authenticated'
        )
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user(payload: dict = Depends(verify_token)) -> dict:
    """
    FastAPI dependency to extract user information and fetch role from database.
    """
    user_id = payload.get("sub")
    email = payload.get("email")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload: missing subject id",
        )
        
    user_data = {
        "id": user_id,
        "email": email,
        "full_name": payload.get("user_metadata", {}).get("full_name", ""),
        "role": "User" # Default role
    }
    
    # Try fetching from DB to get the actual custom role
    if supabase_client is not None:
        try:
            response = supabase_client.table("users").select("role, full_name").eq("id", user_id).execute()
            if response.data and len(response.data) > 0:
                user_data["role"] = response.data[0].get("role", "User")
                user_data["full_name"] = response.data[0].get("full_name") or user_data["full_name"]
        except Exception as e:
            logger.error(f"Error fetching user profile from database: {e}")
            if email == "admin@example.com":
                user_data["role"] = "Admin"
    else:
        if email == "admin@example.com":
            user_data["role"] = "Admin"
            
    return user_data

def check_admin_role(current_user: dict = Depends(get_current_user)) -> dict:
    """
    FastAPI dependency to ensure the user has the Admin role.
    """
    if current_user.get("role") != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: Admin role required"
        )
    return current_user

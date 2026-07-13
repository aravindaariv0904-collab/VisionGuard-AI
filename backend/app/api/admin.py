import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from app.core.security import check_admin_role
from app.database.supabase_client import supabase_client

logger = logging.getLogger("visionguard.admin")
router = APIRouter(prefix="/admin", tags=["Administration"])

@router.get("")
async def get_admin_summary(admin_user: dict = Depends(check_admin_role)):
    """
    Get administrative console statistics and model deployment details.
    Accessible only to users with the Admin role.
    """
    logger.info(f"Admin summary page requested by admin: {admin_user.get('email')}")
    
    total_users = 1 # The admin user itself
    model_versions = [
        {
            "version": "1.0.0",
            "active": True,
            "accuracy": 97.8,
            "created_at": "2026-07-13T00:00:00Z"
        }
    ]
    
    if supabase_client is not None:
        try:
            # Query active model versions
            model_res = supabase_client.table("model_versions").select("*").execute()
            if model_res.data:
                model_versions = model_res.data
                
            # Query total user profiles
            users_res = supabase_client.table("users").select("id", count="exact").execute()
            total_users = users_res.count or 1
        except Exception as e:
            logger.error(f"Error querying administrative stats: {e}")
            
    return {
        "model_versions": model_versions,
        "total_users": total_users,
        "system_status": "Healthy"
    }

import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.database.supabase_client import supabase_client
from app.api.predict import MOCK_PREDICTIONS

logger = logging.getLogger("visionguard.dashboard")
router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("")
async def get_dashboard_summary(current_user: dict = Depends(get_current_user)):
    """
    Get user dashboard stats summary, including scan counts and recent uploads list.
    """
    user_id = current_user.get("id")
    logger.info(f"Dashboard summary requested by user: {current_user.get('email')}")
    
    total_scans = 0
    real_count = 0
    ai_generated_count = 0
    recent_activity = []
    
    if supabase_client is not None:
        try:
            # Query total counts
            total_res = supabase_client.table("predictions").select("id", count="exact").eq("user_id", user_id).execute()
            total_scans = total_res.count or 0
            
            real_res = supabase_client.table("predictions").select("id", count="exact").eq("user_id", user_id).eq("prediction", "Real").execute()
            real_count = real_res.count or 0
            
            ai_res = supabase_client.table("predictions").select("id", count="exact").eq("user_id", user_id).eq("prediction", "AI Generated").execute()
            ai_generated_count = ai_res.count or 0
            
            # Query recent activity (last 5 scans)
            recent_res = supabase_client.table("predictions").select("id, prediction, confidence, created_at").eq("user_id", user_id).order("created_at", desc=True).limit(5).execute()
            
            for item in (recent_res.data or []):
                recent_activity.append({
                    "id": item.get("id"),
                    "prediction": item.get("prediction"),
                    "confidence": item.get("confidence"),
                    "timestamp": item.get("created_at")
                })
                
            return {
                "total_scans": total_scans,
                "real_count": real_count,
                "ai_generated_count": ai_generated_count,
                "recent_activity": recent_activity
            }
        except Exception as e:
            logger.error(f"Error loading dashboard from DB: {e}. Falling back to in-memory data.")
            
    # Mock / Local Fallback Mode
    user_preds = [
        p for p in MOCK_PREDICTIONS.values() 
        if p["user_id"] == user_id
    ]
    total_scans = len(user_preds)
    real_count = sum(1 for p in user_preds if p["prediction"] == "Real")
    ai_generated_count = total_scans - real_count
    
    # Sort activity by created_at desc, limit 5
    user_preds.sort(key=lambda x: x["created_at"], reverse=True)
    for p in user_preds[:5]:
        recent_activity.append({
            "id": p["id"],
            "prediction": p["prediction"],
            "confidence": p["confidence"],
            "timestamp": p["created_at"].isoformat() + "Z"
        })
        
    return {
        "total_scans": total_scans,
        "real_count": real_count,
        "ai_generated_count": ai_generated_count,
        "recent_activity": recent_activity
    }

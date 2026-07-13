import logging
from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.database.supabase_client import supabase_client
from app.api.predict import MOCK_PREDICTIONS

logger = logging.getLogger("visionguard.analytics")
router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("")
async def get_analytics(current_user: dict = Depends(get_current_user)):
    """
    Get detailed prediction trends, accuracy benchmarks, and distribution stats.
    """
    user_id = current_user.get("id")
    logger.info(f"Analytics requested by user: {current_user.get('email')}")
    
    accuracy_rate = 97.8 # Base benchmark
    avg_processing_time = 0.42
    distribution = {"real": 50.0, "ai": 50.0}
    monthly_activity = [{"month": "July", "scans": 0}]
    
    # 1. Fetch details from database if configured
    if supabase_client is not None:
        try:
            # Query avg processing time
            time_res = supabase_client.table("predictions").select("processing_time").eq("user_id", user_id).execute()
            if time_res.data and len(time_res.data) > 0:
                times = [item.get("processing_time", 0) for item in time_res.data]
                avg_processing_time = round(sum(times) / len(times), 2)
                
            # Distribution
            real_res = supabase_client.table("predictions").select("id", count="exact").eq("user_id", user_id).eq("prediction", "Real").execute()
            total_res = supabase_client.table("predictions").select("id", count="exact").eq("user_id", user_id).execute()
            
            real_count = real_res.count or 0
            total_count = total_res.count or 0
            
            if total_count > 0:
                real_pct = round((real_count / total_count) * 100, 1)
                distribution = {
                    "real": real_pct,
                    "ai": round(100.0 - real_pct, 1)
                }
                
            monthly_activity = [{"month": datetime.utcnow().strftime("%B"), "scans": total_count}]
            
            return {
                "accuracy_rate": accuracy_rate,
                "average_processing_time": avg_processing_time,
                "monthly_activity": monthly_activity,
                "distribution": distribution
            }
        except Exception as e:
            logger.error(f"Error loading analytics from DB: {e}. Falling back to mock analytics calculation.")
            
    # 2. Local Fallback Mode
    user_preds = [p for p in MOCK_PREDICTIONS.values() if p["user_id"] == user_id]
    total_count = len(user_preds)
    
    if total_count > 0:
        times = [p["processing_time"] for p in user_preds]
        avg_processing_time = round(sum(times) / len(times), 2)
        
        real_count = sum(1 for p in user_preds if p["prediction"] == "Real")
        real_pct = round((real_count / total_count) * 100, 1)
        distribution = {
            "real": real_pct,
            "ai": round(100.0 - real_pct, 1)
        }
        
    monthly_activity = [{"month": "July", "scans": total_count}]
    
    return {
        "accuracy_rate": accuracy_rate,
        "average_processing_time": avg_processing_time,
        "monthly_activity": monthly_activity,
        "distribution": distribution
    }

import uuid
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from app.core.config import settings
from app.core.security import get_current_user
from app.database.supabase_client import supabase_client
from app.services.prediction_service import predict_image
from app.services.storage_service import upload_file
from app.schemas.prediction import PredictionResponse, PredictionDetailResponse, HistoryResponse, HistoryItem

logger = logging.getLogger("visionguard.predict")
router = APIRouter(tags=["Predictions & Analysis"])

# In-memory mock store for local/testing mode without Supabase connection
MOCK_PREDICTIONS = {}

# Allowed mime types
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "image/webp"]

@router.post("/predict", response_model=PredictionResponse)
async def predict(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Uploads an image, runs the AI authenticity classifier, 
    generates a Grad-CAM heatmap, uploads all assets, and records details in the database.
    """
    logger.info(f"Prediction requested by user: {current_user.get('email')}, file: {file.filename}")
    
    # 1. Validation
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only JPG, PNG, WEBP are supported."
        )
        
    # Read file content
    try:
        contents = await file.read()
        file_size = len(contents)
    except Exception as e:
        logger.error(f"Failed to read upload: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not read uploaded image file."
        )
        
    if file_size > 10 * 1024 * 1024: # 10MB limit
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds limit of 10MB."
        )
        
    # 2. Upload Original Image
    try:
        original_image_url = upload_file(
            bucket_name="original-images",
            file_bytes=contents,
            file_name=file.filename,
            mime_type=file.content_type
        )
    except Exception as upload_err:
        logger.error(f"Original image upload failed: {upload_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload original image."
        )
        
    # 3. Call AI Inference
    try:
        prediction_label, confidence, heatmap_bytes, overlay_bytes, processing_time = predict_image(contents)
    except Exception as ai_err:
        logger.error(f"AI prediction processing failed: {ai_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error running AI classification."
        )
        
    # 4. Upload Heatmap and Overlay Images
    try:
        heatmap_url = upload_file(
            bucket_name="heatmaps",
            file_bytes=heatmap_bytes,
            file_name=f"heatmap_{uuid.uuid4()}.png",
            mime_type="image/png"
        )
        
        overlay_url = upload_file(
            bucket_name="heatmaps",
            file_bytes=overlay_bytes,
            file_name=f"overlay_{uuid.uuid4()}.png",
            mime_type="image/png"
        )
    except Exception as heatmap_upload_err:
        logger.error(f"Heatmap overlays upload failed: {heatmap_upload_err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload generated analysis heatmaps."
        )
        
    # 5. Persist to Database or Fallback
    prediction_id = str(uuid.uuid4())
    created_at = datetime.utcnow()
    
    if supabase_client is not None:
        try:
            # Insert uploads record
            supabase_client.table("uploads").insert({
                "user_id": current_user.get("id"),
                "file_name": file.filename,
                "file_size": file_size,
                "mime_type": file.content_type,
                "storage_path": original_image_url
            }).execute()
            
            # Insert predictions record
            pred_response = supabase_client.table("predictions").insert({
                "id": prediction_id,
                "user_id": current_user.get("id"),
                "original_image_url": original_image_url,
                "prediction": prediction_label,
                "confidence": confidence,
                "processing_time": processing_time,
                "model_version": settings.MODEL_VERSION
            }).execute()
            
            if pred_response.data and len(pred_response.data) > 0:
                prediction_id = pred_response.data[0].get("id", prediction_id)
                
            # Insert heatmaps record
            supabase_client.table("heatmaps").insert({
                "prediction_id": prediction_id,
                "heatmap_url": heatmap_url,
                "overlay_url": overlay_url
            }).execute()
            
        except Exception as db_err:
            logger.error(f"Database insertion failed: {db_err}. Continuing with local caching.")
            
    # Always keep local copy in memory for testing/fallback accessibility
    record = {
        "id": prediction_id,
        "user_id": current_user.get("id"),
        "original_image_url": original_image_url,
        "prediction": prediction_label,
        "confidence": confidence,
        "heatmap_url": heatmap_url,
        "overlay_url": overlay_url,
        "processing_time": processing_time,
        "model_version": settings.MODEL_VERSION,
        "created_at": created_at
    }
    MOCK_PREDICTIONS[prediction_id] = record
    
    return PredictionResponse(
        id=prediction_id,
        prediction=prediction_label,
        confidence=confidence,
        heatmap_url=heatmap_url,
        overlay_url=overlay_url,
        processing_time=processing_time,
        model_version=settings.MODEL_VERSION,
        created_at=created_at
    )

@router.get("/prediction/{id}", response_model=PredictionDetailResponse)
async def get_prediction_detail(
    id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get full details of a specific prediction.
    """
    logger.info(f"Details requested for prediction ID: {id} by user: {current_user.get('email')}")
    
    # Check in-memory store first
    if id in MOCK_PREDICTIONS:
        rec = MOCK_PREDICTIONS[id]
        # Check ownership unless admin
        if rec["user_id"] == current_user.get("id") or current_user.get("role") == "Admin":
            return PredictionDetailResponse(**rec)
            
    # Fetch from Supabase
    if supabase_client is not None:
        try:
            pred_res = supabase_client.table("predictions").select("*").eq("id", id).execute()
            if pred_res.data and len(pred_res.data) > 0:
                pred = pred_res.data[0]
                
                # Check ownership
                if pred.get("user_id") != current_user.get("id") and current_user.get("role") != "Admin":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access forbidden: You do not own this prediction."
                    )
                    
                # Fetch heatmaps URL
                heat_res = supabase_client.table("heatmaps").select("*").eq("prediction_id", id).execute()
                heatmap_url = ""
                overlay_url = ""
                if heat_res.data and len(heat_res.data) > 0:
                    heatmap_url = heat_res.data[0].get("heatmap_url", "")
                    overlay_url = heat_res.data[0].get("overlay_url", "")
                    
                return PredictionDetailResponse(
                    id=pred.get("id"),
                    original_image_url=pred.get("original_image_url"),
                    prediction=pred.get("prediction"),
                    confidence=pred.get("confidence"),
                    heatmap_url=heatmap_url,
                    overlay_url=overlay_url,
                    processing_time=pred.get("processing_time"),
                    model_version=pred.get("model_version"),
                    created_at=datetime.fromisoformat(pred.get("created_at").replace("Z", "+00:00"))
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error loading prediction details from database: {e}")
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Prediction record not found"
    )

@router.get("/history", response_model=HistoryResponse)
async def get_history(
    page: int = 1,
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user history of scans (paginated).
    """
    logger.info(f"History list requested by user: {current_user.get('email')}, page={page}, limit={limit}")
    
    # 1. Fetch from Supabase if active
    if supabase_client is not None:
        try:
            start_row = (page - 1) * limit
            end_row = start_row + limit - 1
            
            # Query count
            count_res = supabase_client.table("predictions").select("id", count="exact").eq("user_id", current_user.get("id")).execute()
            total = count_res.count if count_res.count is not None else 0
            
            # Query data paginated
            data_res = supabase_client.table("predictions").select("*").eq("user_id", current_user.get("id")).order("created_at", desc=True).range(start_row, end_row).execute()
            
            results = []
            for item in (data_res.data or []):
                results.append(
                    HistoryItem(
                        id=item.get("id"),
                        original_image_url=item.get("original_image_url"),
                        prediction=item.get("prediction"),
                        confidence=item.get("confidence"),
                        created_at=datetime.fromisoformat(item.get("created_at").replace("Z", "+00:00"))
                    )
                )
                
            return HistoryResponse(
                total=total,
                page=page,
                limit=limit,
                results=results
            )
        except Exception as e:
            logger.error(f"Error querying history from database: {e}. Falling back to in-memory store.")
            
    # 2. Local Fallback queries from memory
    user_records = [
        HistoryItem(
            id=rec["id"],
            original_image_url=rec["original_image_url"],
            prediction=rec["prediction"],
            confidence=rec["confidence"],
            created_at=rec["created_at"]
        )
        for rec in MOCK_PREDICTIONS.values()
        if rec["user_id"] == current_user.get("id")
    ]
    # Sort by date desc
    user_records.sort(key=lambda r: r.created_at, reverse=True)
    
    total = len(user_records)
    start_row = (page - 1) * limit
    end_row = start_row + limit
    paginated_records = user_records[start_row:end_row]
    
    return HistoryResponse(
        total=total,
        page=page,
        limit=limit,
        results=paginated_records
    )

import io
import uuid
import logging
import zipfile
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks, status
from app.core.config import settings
from app.core.security import get_current_user
from app.database.supabase_client import supabase_client
from app.services.prediction_service import predict_image
from app.services.storage_service import upload_file
from app.schemas.batch import BatchJobStartResponse, BatchJobStatusResponse, BatchResultItem

logger = logging.getLogger("visionguard.batch")
router = APIRouter(prefix="/batch", tags=["Batch Processing"])

# Mock storage for batch jobs in memory
MOCK_BATCH_JOBS = {}

# background worker task to process images asynchronously
def process_batch_job(job_id: str, files_data: List[tuple], user_id: str):
    """
    Background worker that iterates through images, runs AI prediction, 
    uploads images/heatmaps, and stores the results.
    files_data is a list of tuples: (filename, content_bytes, content_type)
    """
    logger.info(f"Starting async processing for Batch Job ID: {job_id}")
    
    # Update status to PROCESSING
    if job_id in MOCK_BATCH_JOBS:
        MOCK_BATCH_JOBS[job_id]["status"] = "PROCESSING"
        
    if supabase_client is not None:
        try:
            supabase_client.table("batch_jobs").update({
                "status": "PROCESSING",
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", job_id).execute()
        except Exception as e:
            logger.error(f"Error updating batch job to PROCESSING in DB: {e}")
            
    processed_count = 0
    results_list = []
    
    for filename, contents, content_type in files_data:
        prediction_id = str(uuid.uuid4())
        try:
            # 1. Upload original image
            original_image_url = upload_file(
                bucket_name="batch-images",
                file_bytes=contents,
                file_name=filename,
                mime_type=content_type
            )
            
            # 2. Run prediction
            prediction_label, confidence, heatmap_bytes, overlay_bytes, processing_time = predict_image(contents)
            
            # 3. Upload heatmaps
            heatmap_url = upload_file(
                bucket_name="heatmaps",
                file_bytes=heatmap_bytes,
                file_name=f"heatmap_batch_{uuid.uuid4()}.png",
                mime_type="image/png"
            )
            overlay_url = upload_file(
                bucket_name="heatmaps",
                file_bytes=overlay_bytes,
                file_name=f"overlay_batch_{uuid.uuid4()}.png",
                mime_type="image/png"
            )
            
            # 4. Save Prediction to DB
            if supabase_client is not None:
                try:
                    supabase_client.table("predictions").insert({
                        "id": prediction_id,
                        "user_id": user_id,
                        "original_image_url": original_image_url,
                        "prediction": prediction_label,
                        "confidence": confidence,
                        "processing_time": processing_time,
                        "model_version": settings.MODEL_VERSION
                    }).execute()
                    
                    supabase_client.table("heatmaps").insert({
                        "prediction_id": prediction_id,
                        "heatmap_url": heatmap_url,
                        "overlay_url": overlay_url
                    }).execute()
                    
                    supabase_client.table("batch_results").insert({
                        "job_id": job_id,
                        "prediction_id": prediction_id,
                        "status": "SUCCESS"
                    }).execute()
                except Exception as db_err:
                    logger.error(f"Failed saving batch prediction item to DB: {db_err}")
            
            results_list.append(
                BatchResultItem(
                    id=prediction_id,
                    prediction=prediction_label,
                    confidence=f"{confidence:.1f}%",
                    status="SUCCESS"
                )
            )
            
        except Exception as err:
            logger.error(f"Error processing batch item {filename}: {err}")
            if supabase_client is not None:
                try:
                    supabase_client.table("batch_results").insert({
                        "job_id": job_id,
                        "prediction_id": None,
                        "status": "FAILED",
                        "error_message": str(err)
                    }).execute()
                except Exception as db_err:
                    logger.error(f"Failed logging batch result failure in DB: {db_err}")
                    
            results_list.append(
                BatchResultItem(
                    status="FAILED",
                    error_message=str(err)
                )
            )
            
        processed_count += 1
        
        # Update progress counter
        if job_id in MOCK_BATCH_JOBS:
            MOCK_BATCH_JOBS[job_id]["processed_images"] = processed_count
            MOCK_BATCH_JOBS[job_id]["results"] = results_list
            
        if supabase_client is not None:
            try:
                supabase_client.table("batch_jobs").update({
                    "processed_images": processed_count,
                    "updated_at": datetime.utcnow().isoformat()
                }).eq("id", job_id).execute()
            except Exception as e:
                logger.error(f"Error updating batch job progress in DB: {e}")
                
    # Finalize job status
    final_status = "COMPLETED" if any(r.status == "SUCCESS" for r in results_list) else "FAILED"
    if job_id in MOCK_BATCH_JOBS:
        MOCK_BATCH_JOBS[job_id]["status"] = final_status
        
    if supabase_client is not None:
        try:
            supabase_client.table("batch_jobs").update({
                "status": final_status,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", job_id).execute()
            
            # Send Notification
            supabase_client.table("notifications").insert({
                "user_id": user_id,
                "title": "Batch Job Finished",
                "message": f"Batch prediction job {job_id[:8]} finished with status {final_status}."
            }).execute()
        except Exception as e:
            logger.error(f"Error finalizing batch job in DB: {e}")
            
    logger.info(f"Finished async processing for Batch Job ID: {job_id}. Status: {final_status}")


@router.post("", response_model=BatchJobStartResponse, status_code=status.HTTP_202_ACCEPTED)
async def start_batch_job(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(None),
    zip_file: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Accepts multiple image uploads or a single ZIP file containing images.
    Extracts images and queues them for asynchronous batch processing.
    """
    logger.info(f"Batch request from user: {current_user.get('email')}")
    
    files_to_process = []
    
    # 1. Parse ZIP file if uploaded
    if zip_file is not None:
        if not zip_file.filename.endswith(".zip"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Zip file must have a .zip extension."
            )
        try:
            zip_contents = await zip_file.read()
            with zipfile.ZipFile(io.BytesIO(zip_contents)) as z:
                for name in z.namelist():
                    # Ignore directory paths, check for images
                    if not name.endswith("/") and name.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        file_data = z.read(name)
                        # Determine MIME type
                        ext = name.split(".")[-1].lower()
                        mime = f"image/{ext}" if ext != "jpg" else "image/jpeg"
                        files_to_process.append((os.path.basename(name), file_data, mime))
        except Exception as e:
            logger.error(f"Error parsing ZIP file: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Could not extract files from zip: {e}"
            )
            
    # 2. Parse Multiple Files if uploaded
    elif files is not None and len(files) > 0 and files[0].filename != "":
        for file in files:
            if file.content_type not in ["image/jpeg", "image/png", "image/webp"]:
                continue # Skip invalid files
            try:
                contents = await file.read()
                files_to_process.append((file.filename, contents, file.content_type))
            except Exception as e:
                logger.warning(f"Skipping unreadable file {file.filename}: {e}")
                
    if len(files_to_process) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No valid image files provided (supported: JPG, PNG, WEBP, or ZIP containing images)."
        )
        
    # Limit to 50 images per batch to prevent server overloading
    if len(files_to_process) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Batch limit exceeded. Max 50 images per batch job."
        )
        
    job_id = str(uuid.uuid4())
    total_images = len(files_to_process)
    
    # 3. Create job in Database
    if supabase_client is not None:
        try:
            supabase_client.table("batch_jobs").insert({
                "id": job_id,
                "user_id": current_user.get("id"),
                "status": "PENDING",
                "total_images": total_images,
                "processed_images": 0
            }).execute()
        except Exception as db_err:
            logger.error(f"Error saving batch job status to DB: {db_err}")
            
    # Store locally in mock
    MOCK_BATCH_JOBS[job_id] = {
        "job_id": job_id,
        "status": "PENDING",
        "total_images": total_images,
        "processed_images": 0,
        "results": [],
        "user_id": current_user.get("id")
    }
    
    # 4. Trigger background processing task
    background_tasks.add_task(
        process_batch_job,
        job_id=job_id,
        files_data=files_to_process,
        user_id=current_user.get("id")
    )
    
    return BatchJobStartResponse(
        job_id=job_id,
        status="PENDING",
        total_images=total_images,
        message="Batch processing started asynchronously."
    )

@router.get("/{job_id}", response_model=BatchJobStatusResponse)
async def get_batch_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Retrieve the status and results of a queued batch prediction job.
    """
    logger.info(f"Batch status requested for ID: {job_id} by user: {current_user.get('email')}")
    
    # Check mock store first
    if job_id in MOCK_BATCH_JOBS:
        job = MOCK_BATCH_JOBS[job_id]
        if job["user_id"] == current_user.get("id") or current_user.get("role") == "Admin":
            return BatchJobStatusResponse(**job)
            
    # Fetch from Supabase
    if supabase_client is not None:
        try:
            job_res = supabase_client.table("batch_jobs").select("*").eq("id", job_id).execute()
            if job_res.data and len(job_res.data) > 0:
                job = job_res.data[0]
                
                # Check ownership
                if job.get("user_id") != current_user.get("id") and current_user.get("role") != "Admin":
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access forbidden: You do not own this batch job."
                    )
                    
                # Fetch results
                res_data = supabase_client.table("batch_results").select(
                    "status, error_message, predictions(prediction, confidence)"
                ).eq("job_id", job_id).execute()
                
                results = []
                for item in (res_data.data or []):
                    pred = item.get("predictions") or {}
                    results.append(
                        BatchResultItem(
                            prediction=pred.get("prediction"),
                            confidence=f"{pred.get('confidence'):.1f}%" if pred.get("confidence") is not None else None,
                            status=item.get("status"),
                            error_message=item.get("error_message")
                        )
                    )
                    
                return BatchJobStatusResponse(
                    job_id=job_id,
                    status=job.get("status"),
                    total_images=job.get("total_images"),
                    processed_images=job.get("processed_images"),
                    results=results
                )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error querying batch status from DB: {e}")
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Batch job not found."
    )

import os
import uuid
import logging
from app.core.config import settings
from app.database.supabase_client import supabase_client

logger = logging.getLogger("visionguard.storage")

# Ensure static directories exist for local file serving fallback
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static")
BUCKETS = ["original-images", "heatmaps", "reports", "batch-images", "avatars"]

for bucket in BUCKETS:
    os.makedirs(os.path.join(STATIC_DIR, bucket), exist_ok=True)

def upload_file(bucket_name: str, file_bytes: bytes, file_name: str, mime_type: str) -> str:
    """
    Uploads a file to a Supabase bucket, or falls back to local static file serving.
    Returns: The public URL of the uploaded file.
    """
    # Generate unique filename to avoid collision
    ext = os.path.splitext(file_name)[1] or ".png"
    unique_name = f"{uuid.uuid4()}{ext}"
    
    if supabase_client is not None:
        try:
            # Upload to Supabase Storage
            res = supabase_client.storage.from_(bucket_name).upload(
                path=unique_name,
                file=file_bytes,
                file_options={"content-type": mime_type, "x-upsert": "true"}
            )
            
            # Get public URL
            public_url = supabase_client.storage.from_(bucket_name).get_public_url(unique_name)
            logger.info(f"File uploaded to Supabase storage bucket '{bucket_name}': {public_url}")
            return public_url
        except Exception as e:
            logger.error(f"Failed to upload to Supabase storage: {e}. Falling back to local storage.")
            
    # Local Storage Fallback
    local_path = os.path.join(STATIC_DIR, bucket_name, unique_name)
    try:
        with open(local_path, "wb") as f:
            f.write(file_bytes)
        
        # Local serving URL
        local_url = f"http://localhost:{settings.PORT}/static/{bucket_name}/{unique_name}"
        logger.info(f"File saved to local storage fallback: {local_url}")
        return local_url
    except Exception as local_err:
        logger.error(f"Failed to save local file fallback: {local_err}")
        raise ValueError(f"Could not save uploaded file: {local_err}")

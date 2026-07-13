from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class BatchJobStartResponse(BaseModel):
    job_id: str
    status: str
    total_images: int
    message: str

class BatchResultItem(BaseModel):
    id: Optional[str] = None
    prediction: Optional[str] = None
    confidence: Optional[str] = None # e.g. "97.8%"
    status: str # SUCCESS or FAILED
    error_message: Optional[str] = None

class BatchJobStatusResponse(BaseModel):
    job_id: str
    status: str
    total_images: int
    processed_images: int
    results: List[BatchResultItem]

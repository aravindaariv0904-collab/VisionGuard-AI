from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PredictionResponse(BaseModel):
    id: str
    prediction: str
    confidence: float
    heatmap_url: str
    overlay_url: str
    processing_time: float
    model_version: str
    created_at: datetime

class PredictionDetailResponse(BaseModel):
    id: str
    original_image_url: str
    prediction: str
    confidence: float
    heatmap_url: str
    overlay_url: str
    processing_time: float
    model_version: str
    created_at: datetime

class HistoryItem(BaseModel):
    id: str
    original_image_url: str
    prediction: str
    confidence: float
    created_at: datetime

class HistoryResponse(BaseModel):
    total: int
    page: int
    limit: int
    results: List[HistoryItem]

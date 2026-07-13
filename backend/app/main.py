import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api import auth, predict, batch, dashboard, analytics, admin, health

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("visionguard.main")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Explainable AI Image Authenticity Detection Platform API",
    version=settings.MODEL_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS Middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount local static files directory for storage fallbacks
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR, exist_ok=True)
    
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
logger.info(f"Mounted local static storage directory: {STATIC_DIR}")

# Include Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(batch.router)
app.include_router(dashboard.router)
app.include_router(analytics.router)
app.include_router(admin.router)

@app.on_event("startup")
async def startup_event():
    logger.info("VisionGuard AI API backend server is starting up...")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("VisionGuard AI API backend server is shutting down...")

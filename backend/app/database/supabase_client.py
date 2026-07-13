import logging
from supabase import create_client, Client
from app.core.config import settings

logger = logging.getLogger("visionguard.database")

# Initialize client
supabase_client: Client = None

try:
    if settings.SUPABASE_URL and settings.SUPABASE_ANON_KEY and "placeholder" not in settings.SUPABASE_URL:
        supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
        logger.info("Supabase client initialized successfully.")
    else:
        logger.warning("Supabase URL or Anon Key is missing or placeholder. Running with mock database mode.")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase_client = None

def get_supabase() -> Client:
    if supabase_client is None:
        raise ValueError("Supabase client is not initialized. Please verify your credentials in .env.")
    return supabase_client

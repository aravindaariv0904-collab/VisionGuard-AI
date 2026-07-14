import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"))

class Settings(BaseSettings):
    PROJECT_NAME: str = "VisionGuard AI"
    API_V1_STR: str = ""
    
    # Server configuration
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    DEBUG: bool = True
    
    # Supabase Credentials (optional defaults for local testing if not supplied)
    SUPABASE_URL: str = "https://placeholder-project.supabase.co"
    SUPABASE_ANON_KEY: str = "placeholder-anon-key"
    SUPABASE_SERVICE_ROLE_KEY: str = "placeholder-service-role-key"
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"
    
    # JWT Verification
    JWT_SECRET: str = "placeholder-jwt-secret-placeholder-jwt-secret-placeholder-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    
    # Model configuration
    MODEL_VERSION: str = "6630a40"
    ACCURACY_THRESHOLD: float = 0.5

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"

settings = Settings()

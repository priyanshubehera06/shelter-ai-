"""
config.py — Application configuration and environment settings for ShelterAI FastAPI backend.
"""

import os
from typing import List
from pydantic import BaseModel


def _get_cors_origins() -> List[str]:
    """Dynamically resolves allowed CORS origins from environment and defaults."""
    origins: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    
    # Check FRONTEND_ORIGIN env var (e.g. from Vercel deployment)
    frontend_origin = os.getenv("FRONTEND_ORIGIN")
    if frontend_origin:
        for origin in frontend_origin.split(","):
            cleaned = origin.strip().rstrip("/")
            if cleaned and cleaned not in origins:
                origins.append(cleaned)
                
    # Check CORS_ORIGINS env var
    cors_env = os.getenv("CORS_ORIGINS")
    if cors_env:
        for origin in cors_env.split(","):
            cleaned = origin.strip().rstrip("/")
            if cleaned and cleaned not in origins:
                origins.append(cleaned)
                
    # In development mode, allow wildcard if no specific origins are set
    env_mode = os.getenv("ENVIRONMENT", "development").lower()
    if env_mode == "development" and "*" not in origins:
        origins.append("*")
        
    return origins


class Settings(BaseModel):
    PROJECT_NAME: str = "ShelterAI API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Server network settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = _get_cors_origins()
    
    # Path configurations
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    DATABASE_PATH: str = os.path.join(BASE_DIR, "database", "shelter.db")


settings = Settings()

"""
config.py — Application configuration and environment settings for ShelterAI FastAPI backend.
"""

import os
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "ShelterAI API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "*",
    ]
    
    # Path configurations
    BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    DATA_DIR: str = os.path.join(BASE_DIR, "data")
    DATABASE_PATH: str = os.path.join(BASE_DIR, "database", "shelter.db")


settings = Settings()

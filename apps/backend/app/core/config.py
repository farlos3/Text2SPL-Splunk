import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Chat Backend API"
    
    # CORS Settings
    FRONTEND_ORIGIN: str = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # External API Keys
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Add frontend origin to allowed origins if not already present
        if self.FRONTEND_ORIGIN not in self.ALLOWED_ORIGINS:
            self.ALLOWED_ORIGINS.append(self.FRONTEND_ORIGIN)

    class Config:
        env_file = ".env"

settings = Settings()

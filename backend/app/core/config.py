import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = Field(default="Vishakan Biotech Smart Farming Assistant Backend")
    DEBUG: bool = Field(default=True)
    
    # Database Configuration
    DATABASE_URL: str = Field(default="postgresql://postgres:postgres@localhost:5432/vishakan_db")
    
    # Security Configs
    SECRET_KEY: str = Field(default="")
    ALGORITHM: str = Field(default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)
    
    # Redis Configurations
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # Third-party Integrations
    GEMINI_API_KEY: str = Field(default="")
    
    # Upload Directories
    UPLOAD_DIR: str = Field(default="backend/data/uploads")
    VECTOR_DB_DIR: str = Field(default="backend/vector_db/chroma_store")
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
os.makedirs("backend/app/ml_models", exist_ok=True)
os.makedirs("backend/data", exist_ok=True)

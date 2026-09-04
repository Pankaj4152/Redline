from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Base directory of the backend package
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    """
    Application Settings loaded from environment variables and .env file.
    Validates configuration types automatically using Pydantic.
    """
    APP_NAME: str = "Redline Backend"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    
    # AI Engine Config
    GEMINI_API_KEY: str = "mock_key_for_dev"
    
    # Security Guardrails
    MAX_REPO_SIZE_MB: int = 50
    MAX_TOKEN_BUDGET: int = 15000

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

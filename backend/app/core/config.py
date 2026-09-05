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
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = "Redline - AI-Powered Pre-Flight Testing & Red-Teaming Tool for AI-Native Coding Assessments"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # AI Engine Config & Mock Execution Flag
    GEMINI_API_KEY: str | None = None
    USE_MOCK_LLM: bool = True
    
    # Security Guardrails
    MAX_REPO_SIZE_MB: int = 50
    MAX_TOKEN_BUDGET: int = 15000

    model_config = SettingsConfigDict(
        env_file=str(BACKEND_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

from typing import List, Union, Optional
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "CareIntel AI - Healthcare Intelligence"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Database URL: Supports PostgreSQL (e.g. postgresql://user:pass@localhost:5432/db)
    # or SQLite fallback (sqlite:///./careintel.db)
    DATABASE_URL: str = "sqlite:///./careintel.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_url(cls, v: str) -> str:
        """
        Railway and other PaaS providers supply PostgreSQL connection strings
        starting with 'postgres://'. SQLAlchemy 2.0 requires 'postgresql://'.
        """
        if isinstance(v, str) and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v
    
    # CORS
    FRONTEND_URL: Optional[str] = None
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "*"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        origins = []
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                try:
                    origins = json.loads(v)
                except Exception:
                    origins = [v]
            else:
                origins = [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            origins = list(v)
        else:
            origins = ["*"]
            
        # Append FRONTEND_URL if provided in environment
        frontend_url = os.environ.get("FRONTEND_URL")
        if frontend_url and frontend_url.strip():
            cleaned = frontend_url.strip().rstrip("/")
            if cleaned not in origins:
                origins.append(cleaned)
                
        return origins

    # AI Configuration
    AI_PROVIDER: str = "demo"  # "openai" | "gemini" | "demo"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    AI_BASE_URL: str = "https://api.openai.com/v1"

    # Scraper settings
    SCRAPER_TIMEOUT_SECONDS: int = 15
    SCRAPER_USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36 (CareIntel Public Bot 1.0)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

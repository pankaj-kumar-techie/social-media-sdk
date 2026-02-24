import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

# Get the project root directory
ROOT_DIR = Path(__file__).parent.parent

class Settings(BaseSettings):
    # YouTube Configuration
    YOUTUBE_API_KEY: Optional[str] = None

    # Instagram Configuration
    INSTAGRAM_SESSION_ID: Optional[str] = None
    INSTAGRAM_CSRF_TOKEN: Optional[str] = None

    # TikTok Configuration
    TIKTOK_SESSION_ID: Optional[str] = None

    # Global Configuration
    PROXY_URL: Optional[str] = None
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=os.path.join(ROOT_DIR, ".env"),
        env_file_encoding="utf-8", 
        extra="ignore"
    )

settings = Settings()

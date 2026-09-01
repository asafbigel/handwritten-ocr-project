import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

class AppSettings(BaseSettings):
    # API Configuration
    gemini_api_key: str = Field(..., alias="GEMINI_API_KEY")
    gemini_model: str = Field("gemini-2.5-pro", alias="GEMINI_MODEL")
    
    # Execution Limits (NFR4)
    rpm_limit: int = 15
    rpd_limit: int = 1500

    # Path Configuration
    input_dir: str = "input"
    output_dir: str = "output"
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")

# Singleton instance
settings = None
def get_settings():
    global settings
    if settings is None:
        settings = AppSettings()
    return settings
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Find the project root directory
ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or the root .env file."""

    app_name: str = "CareerScout AI API"
    environment: str = "development"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

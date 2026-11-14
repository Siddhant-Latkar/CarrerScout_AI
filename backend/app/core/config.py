from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

# backend/app/core/config.py -> project root is three folders up from this file's folder
ROOT_DIR = Path(__file__).resolve().parents[3]

_DEV_SECRET_KEY = "dev-only-insecure-secret-change-me"


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or the root .env file."""

    app_name: str = "CareerScout AI API"
    environment: str = "development"

    postgres_user: str = "careerscout"
    postgres_password: str = "careerscout_dev_password"
    postgres_db: str = "careerscout"
    postgres_host: str = "localhost"
    postgres_port: int = 5432

    secret_key: str = _DEV_SECRET_KEY
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def reject_default_secret_outside_development(self) -> Self:
        """Stop the app from starting in production with the public development secret."""
        if self.environment != "development" and self.secret_key == _DEV_SECRET_KEY:
            raise ValueError("SECRET_KEY must be set to a private value outside development")
        return self

    @property
    def database_url(self) -> URL:
        """Build the PostgreSQL connection URL safely (special characters are escaped)."""
        return URL.create(
            drivername="postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.postgres_db,
        )


settings = Settings()

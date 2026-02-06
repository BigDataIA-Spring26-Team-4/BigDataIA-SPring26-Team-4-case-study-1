"""
Application configuration using Pydantic v2 for robust validation.
Provides type-safe, validated settings for the PE Org-AI-R Platform.
"""

from typing import Optional, Literal
from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings for the PE Org-AI-R Platform with production-grade validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
    )

    # --- Application Settings ---
    APP_NAME: str = "PE Org-AI-R Platform"
    APP_VERSION: str = "1.0.0"
    APP_ENV: Literal["development", "staging", "production"] = "development"
    DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "console"

    # --- Snowflake Database Settings ---
    SNOWFLAKE_USER: str
    SNOWFLAKE_PASSWORD: SecretStr
    SNOWFLAKE_ACCOUNT: str
    SNOWFLAKE_DATABASE: str = "PE_ORGAIR"
    SNOWFLAKE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_WAREHOUSE: str
    SNOWFLAKE_ROLE: Optional[str] = None

    # --- Redis Cache Settings ---
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = Field(default=6379, ge=1, le=65535)
    REDIS_USERNAME: Optional[str] = None
    REDIS_PASSWORD: Optional[SecretStr] = None
    REDIS_DB: int = Field(default=0, ge=0, le=15)
    REDIS_TTL: int = Field(default=3600, ge=60, le=86400)  # 1 min to 24 hours

    # --- AWS S3 Settings ---
    AWS_ACCESS_KEY_ID: SecretStr
    AWS_SECRET_ACCESS_KEY: SecretStr
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: str

    # --- API Settings ---
    API_RATE_LIMIT: int = Field(default=100, ge=1, le=1000)
    MAX_PAGE_SIZE: int = Field(default=100, ge=1, le=500)

    @property
    def snowflake_url(self) -> str:
        """Construct Snowflake connection URL."""
        return (
            f"snowflake://{self.SNOWFLAKE_USER}:"
            f"{self.SNOWFLAKE_PASSWORD.get_secret_value()}@"
            f"{self.SNOWFLAKE_ACCOUNT}/"
            f"{self.SNOWFLAKE_DATABASE}/"
            f"{self.SNOWFLAKE_SCHEMA}?"
            f"warehouse={self.SNOWFLAKE_WAREHOUSE}"
        )

    @property
    def redis_url(self) -> str:
        """Construct Redis connection URL."""
        if self.REDIS_USERNAME and self.REDIS_PASSWORD:
            return (
                f"redis://{self.REDIS_USERNAME}:"
                f"{self.REDIS_PASSWORD.get_secret_value()}@"
                f"{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            )
        elif self.REDIS_PASSWORD:
            return (
                f"redis://:{self.REDIS_PASSWORD.get_secret_value()}@"
                f"{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
            )
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Returns:
        Settings: Application settings singleton

    Note:
        Settings are cached to avoid repeated environment variable parsing.
        Clear cache with get_settings.cache_clear() if needed.
    """
    return Settings()

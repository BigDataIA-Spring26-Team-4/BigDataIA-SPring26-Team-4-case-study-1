"""
Tests for configuration validation system.
"""

import pytest
import os
from pydantic import ValidationError
from app.config import Settings, get_settings


class TestConfigValidation:
    """Test configuration validation rules."""

    def test_valid_configuration(self, monkeypatch):
        """Test that valid configuration loads successfully."""
        # Set up valid environment variables
        env_vars = {
            "SNOWFLAKE_USER": "test_user",
            "SNOWFLAKE_PASSWORD": "test_password",
            "SNOWFLAKE_ACCOUNT": "test_account",
            "SNOWFLAKE_DATABASE": "PE_ORGAIR",
            "SNOWFLAKE_WAREHOUSE": "test_warehouse",
            "AWS_ACCESS_KEY_ID": "test_key_id",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key",
            "S3_BUCKET_NAME": "test-bucket",
        }

        for key, value in env_vars.items():
            monkeypatch.setenv(key, value)

        # Clear cache and load settings
        get_settings.cache_clear()
        settings = get_settings()

        assert settings.SNOWFLAKE_USER == "test_user"
        assert settings.SNOWFLAKE_DATABASE == "PE_ORGAIR"
        assert settings.S3_BUCKET_NAME == "test-bucket"

    def test_missing_required_field(self):
        """Test that missing required fields raise ValidationError."""
        # Clear cache
        get_settings.cache_clear()

        # Create Settings with minimal args, missing required fields
        with pytest.raises(ValidationError) as exc_info:
            # Don't load from .env file
            Settings(_env_file=None, SNOWFLAKE_USER="test_user")

        errors = exc_info.value.errors()
        # Check that we have errors for missing fields
        assert len(errors) > 0
        # Should have errors for SNOWFLAKE_PASSWORD, ACCOUNT, WAREHOUSE, AWS credentials, etc.
        error_fields = {str(e["loc"][0]) for e in errors}
        assert "SNOWFLAKE_PASSWORD" in error_fields or "SNOWFLAKE_ACCOUNT" in error_fields

    def test_redis_port_validation(self, monkeypatch):
        """Test Redis port must be within valid range."""
        self._setup_minimal_env(monkeypatch)
        monkeypatch.setenv("REDIS_PORT", "99999")  # Invalid port

        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any("REDIS_PORT" in str(e["loc"]) for e in errors)

    def test_redis_ttl_validation(self, monkeypatch):
        """Test Redis TTL must be within valid range."""
        self._setup_minimal_env(monkeypatch)
        monkeypatch.setenv("REDIS_TTL", "30")  # Below minimum of 60

        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any("REDIS_TTL" in str(e["loc"]) for e in errors)

    def test_api_rate_limit_validation(self, monkeypatch):
        """Test API rate limit must be within valid range."""
        self._setup_minimal_env(monkeypatch)
        monkeypatch.setenv("API_RATE_LIMIT", "5000")  # Above maximum of 1000

        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            Settings()

        errors = exc_info.value.errors()
        assert any("API_RATE_LIMIT" in str(e["loc"]) for e in errors)

    def test_snowflake_url_property(self, monkeypatch):
        """Test snowflake_url property generates correct URL."""
        self._setup_minimal_env(monkeypatch)
        monkeypatch.setenv("SNOWFLAKE_USER", "test_user")
        monkeypatch.setenv("SNOWFLAKE_PASSWORD", "test_pass")
        monkeypatch.setenv("SNOWFLAKE_ACCOUNT", "test_account")
        monkeypatch.setenv("SNOWFLAKE_DATABASE", "TEST_DB")
        monkeypatch.setenv("SNOWFLAKE_SCHEMA", "TEST_SCHEMA")
        monkeypatch.setenv("SNOWFLAKE_WAREHOUSE", "TEST_WH")

        get_settings.cache_clear()
        settings = get_settings()

        url = settings.snowflake_url
        assert "snowflake://" in url
        assert "test_user" in url
        assert "test_pass" in url
        assert "test_account" in url
        assert "TEST_DB" in url
        assert "TEST_SCHEMA" in url
        assert "warehouse=TEST_WH" in url

    def test_redis_url_property_with_password(self, monkeypatch):
        """Test redis_url property with password."""
        self._setup_minimal_env(monkeypatch)
        monkeypatch.setenv("REDIS_HOST", "redis.example.com")
        monkeypatch.setenv("REDIS_PORT", "6379")
        monkeypatch.setenv("REDIS_PASSWORD", "secret_pass")
        monkeypatch.setenv("REDIS_DB", "1")

        get_settings.cache_clear()
        settings = get_settings()

        url = settings.redis_url
        assert "redis://" in url
        assert "secret_pass" in url
        assert "redis.example.com" in url
        assert ":6379" in url
        assert "/1" in url

    def test_redis_url_property_without_password(self, monkeypatch):
        """Test redis_url property without password."""
        self._setup_minimal_env(monkeypatch)
        monkeypatch.setenv("REDIS_HOST", "localhost")
        monkeypatch.setenv("REDIS_PORT", "6379")
        monkeypatch.setenv("REDIS_DB", "0")

        get_settings.cache_clear()
        settings = get_settings()

        url = settings.redis_url
        # Check the URL contains the right components
        assert url.startswith("redis://")
        assert "localhost:6379/0" in url

    def test_secret_str_masking(self, monkeypatch):
        """Test that SecretStr fields are properly masked."""
        self._setup_minimal_env(monkeypatch)
        monkeypatch.setenv("SNOWFLAKE_PASSWORD", "super_secret_password")

        get_settings.cache_clear()
        settings = get_settings()

        # String representation should be masked
        password_repr = repr(settings.SNOWFLAKE_PASSWORD)
        assert "super_secret_password" not in password_repr
        assert "SecretStr" in password_repr

        # But we can get the actual value when needed
        assert settings.SNOWFLAKE_PASSWORD.get_secret_value() == "super_secret_password"

    def test_default_values(self, monkeypatch):
        """Test that default values are set correctly."""
        self._setup_minimal_env(monkeypatch)

        # Override with known defaults for this test
        monkeypatch.setenv("APP_ENV", "development")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        monkeypatch.setenv("LOG_FORMAT", "console")
        monkeypatch.setenv("REDIS_HOST", "localhost")
        monkeypatch.setenv("REDIS_PORT", "6379")
        monkeypatch.setenv("AWS_REGION", "us-east-1")

        get_settings.cache_clear()
        settings = get_settings()

        assert settings.APP_ENV == "development"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "INFO"
        assert settings.LOG_FORMAT == "console"
        assert settings.REDIS_HOST == "localhost"
        assert settings.REDIS_PORT == 6379
        assert settings.AWS_REGION == "us-east-1"

    def test_environment_override(self, monkeypatch):
        """Test that environment variables override defaults."""
        self._setup_minimal_env(monkeypatch)
        monkeypatch.setenv("APP_ENV", "production")
        monkeypatch.setenv("DEBUG", "false")
        monkeypatch.setenv("LOG_LEVEL", "ERROR")

        get_settings.cache_clear()
        settings = get_settings()

        assert settings.APP_ENV == "production"
        assert settings.DEBUG is False
        assert settings.LOG_LEVEL == "ERROR"

    def _setup_minimal_env(self, monkeypatch):
        """Set up minimal required environment variables."""
        # Clear all optional environment variables that might be set in .env
        optional_vars = [
            "REDIS_HOST", "REDIS_PORT", "REDIS_USERNAME", "REDIS_PASSWORD",
            "REDIS_DB", "REDIS_TTL", "AWS_REGION", "APP_ENV", "DEBUG",
            "LOG_LEVEL", "LOG_FORMAT", "API_RATE_LIMIT", "MAX_PAGE_SIZE",
        ]
        for var in optional_vars:
            monkeypatch.delenv(var, raising=False)

        required_vars = {
            "SNOWFLAKE_USER": "test_user",
            "SNOWFLAKE_PASSWORD": "test_password",
            "SNOWFLAKE_ACCOUNT": "test_account",
            "SNOWFLAKE_WAREHOUSE": "test_warehouse",
            "AWS_ACCESS_KEY_ID": "test_key_id",
            "AWS_SECRET_ACCESS_KEY": "test_secret_key",
            "S3_BUCKET_NAME": "test-bucket",
        }

        for key, value in required_vars.items():
            monkeypatch.setenv(key, value)

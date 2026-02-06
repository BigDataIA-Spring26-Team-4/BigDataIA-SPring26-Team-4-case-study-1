#!/usr/bin/env python3
"""
Configuration validation script for PE Org-AI-R Platform.

Usage:
    python scripts/validate_config.py

This script validates all configuration settings before application startup.
Use this in CI/CD pipelines to catch configuration errors early.
"""

import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from pydantic import ValidationError
from app.config import get_settings


def main():
    """Validate configuration and print summary."""
    print("=" * 70)
    print("PE Org-AI-R Platform - Configuration Validation")
    print("=" * 70)
    print()

    try:
        settings = get_settings()

        print("✓ Configuration validation successful!")
        print()
        print("Configuration Summary:")
        print("-" * 70)
        print(f"  App Name:           {settings.APP_NAME}")
        print(f"  Version:            {settings.APP_VERSION}")
        print(f"  Environment:        {settings.APP_ENV}")
        print(f"  Debug Mode:         {settings.DEBUG}")
        print(f"  Log Level:          {settings.LOG_LEVEL}")
        print(f"  Log Format:         {settings.LOG_FORMAT}")
        print()
        print(f"  Snowflake Database: {settings.SNOWFLAKE_DATABASE}")
        print(f"  Snowflake Schema:   {settings.SNOWFLAKE_SCHEMA}")
        print(f"  Snowflake Account:  {settings.SNOWFLAKE_ACCOUNT}")
        print()
        print(f"  Redis Host:         {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        print(f"  Redis DB:           {settings.REDIS_DB}")
        print(f"  Redis TTL:          {settings.REDIS_TTL}s")
        print()
        print(f"  AWS Region:         {settings.AWS_REGION}")
        print(f"  S3 Bucket:          {settings.S3_BUCKET_NAME}")
        print()
        print(f"  API Rate Limit:     {settings.API_RATE_LIMIT} req/min")
        print(f"  Max Page Size:      {settings.MAX_PAGE_SIZE}")
        print("-" * 70)
        print()

        # Additional validation checks
        print("Running additional validation checks...")
        print()

        # Check environment-specific requirements
        if settings.APP_ENV == "production":
            if settings.DEBUG:
                print("✗ ERROR: DEBUG mode is enabled in production!")
                return 1
            print("  ✓ Production mode: DEBUG is disabled")

        print()
        print("=" * 70)
        print("All validation checks passed! ✓")
        print("=" * 70)
        return 0

    except ValidationError as e:
        print("✗ Configuration validation FAILED!")
        print()
        print("Errors:")
        print("-" * 70)
        for error in e.errors():
            field = " -> ".join(str(loc) for loc in error["loc"])
            message = error["msg"]
            error_type = error["type"]
            print(f"  Field:   {field}")
            print(f"  Error:   {message}")
            print(f"  Type:    {error_type}")
            print()
        print("=" * 70)
        print("Fix the above errors in your .env file or environment variables.")
        print("=" * 70)
        return 1

    except Exception as e:
        print(f"✗ Unexpected error during validation: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

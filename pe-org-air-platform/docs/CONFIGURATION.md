# Configuration Guide

## Overview

The PE Org-AI-R Platform uses a robust, type-safe configuration system built with **Pydantic v2**. This ensures that all configuration values are validated at application startup, preventing runtime errors due to misconfiguration.

## Key Features

- ✅ **Type Safety**: All configuration values are strongly typed
- ✅ **Validation**: Automatic validation with clear error messages
- ✅ **Security**: Sensitive values (passwords, API keys) use `SecretStr` to prevent accidental exposure
- ✅ **Environment-based**: Configuration loads from environment variables or `.env` files
- ✅ **Fail-fast**: Invalid configurations are caught at startup, not at runtime

## Configuration File

Create a `.env` file in the project root (see `.env.example` for reference):

```bash
# Copy the example and edit with your values
cp .env.example .env
```

## Required Settings

### Snowflake Database

```bash
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ACCOUNT=your_account.region
SNOWFLAKE_DATABASE=PE_ORGAIR
SNOWFLAKE_SCHEMA=PUBLIC
SNOWFLAKE_WAREHOUSE=your_warehouse
```

### Redis Cache

```bash
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_TTL=3600  # Cache TTL in seconds
```

### AWS S3

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name
```

## Validation Rules

The configuration system enforces the following validation rules:

### Redis Settings

- `REDIS_PORT`: Must be between 1 and 65535
- `REDIS_DB`: Must be between 0 and 15
- `REDIS_TTL`: Must be between 60 and 86400 seconds (1 min to 24 hours)

### API Settings

- `API_RATE_LIMIT`: Must be between 1 and 1000 requests per minute
- `MAX_PAGE_SIZE`: Must be between 1 and 500 items

### Environment-Specific Rules

When `APP_ENV=production`:
- `DEBUG` must be `false`

## Usage in Code

```python
from app.config import get_settings

# Get configuration (cached singleton)
settings = get_settings()

# Access values
database_name = settings.SNOWFLAKE_DATABASE
redis_ttl = settings.REDIS_TTL

# Access secrets (use .get_secret_value())
password = settings.SNOWFLAKE_PASSWORD.get_secret_value()
```

## Validating Configuration

Before starting the application, you can validate your configuration:

```bash
python scripts/validate_config.py
```

This will:
- ✓ Check all required fields are present
- ✓ Validate field types and constraints
- ✓ Display a configuration summary
- ✓ Check environment-specific requirements

## Configuration Properties

The `Settings` class provides convenient properties:

### `snowflake_url`

Generates a complete Snowflake connection URL:

```python
settings = get_settings()
print(settings.snowflake_url)
# snowflake://user:password@account/database/schema?warehouse=wh_name
```

### `redis_url`

Generates a complete Redis connection URL:

```python
settings = get_settings()
print(settings.redis_url)
# redis://user:password@localhost:6379/0
```

## Security Best Practices

1. **Never commit `.env` files** - They contain sensitive credentials
2. **Use `SecretStr` fields** - These are automatically masked in logs
3. **Validate in production** - Run `validate_config.py` in CI/CD pipelines
4. **Set production environment** - Use `APP_ENV=production` in production deployments

## Troubleshooting

### ValidationError on Startup

If you see a `ValidationError` when starting the application:

1. Check that all required fields are set in `.env`
2. Verify field values match the expected types
3. Run `python scripts/validate_config.py` for detailed error messages

### Missing Environment Variables

```
pydantic.validation_error: Field required
```

**Solution**: Add the missing field to your `.env` file

### Invalid Value Range

```
pydantic.validation_error: Input should be less than or equal to 65535
```

**Solution**: Adjust the value to fall within the valid range

## Example Configurations

### Development Environment

```bash
APP_ENV=development
DEBUG=true
LOG_LEVEL=DEBUG
LOG_FORMAT=console
REDIS_HOST=localhost
```

### Production Environment

```bash
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
LOG_FORMAT=json
REDIS_HOST=redis.production.internal
```

## Common Mistakes

### ❌ Exposing Secrets in Logs

```python
# WRONG - Exposes password
logger.info("connecting", password=settings.SNOWFLAKE_PASSWORD)
```

```python
# CORRECT - Password is masked
logger.info("connecting", password=settings.SNOWFLAKE_PASSWORD)
# Output: connecting password=SecretStr('**********')
```

### ❌ Hard-coding Configuration

```python
# WRONG
redis_host = "localhost"
```

```python
# CORRECT
settings = get_settings()
redis_host = settings.REDIS_HOST
```

### ❌ Not Validating at Startup

Run the validation script in your CI/CD pipeline:

```bash
# In your deployment script
python scripts/validate_config.py || exit 1
python -m uvicorn app.main:app
```

## References

- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [Environment Variables Best Practices](https://12factor.net/config)

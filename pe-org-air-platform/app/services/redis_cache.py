import hashlib
import json
import asyncio
import functools
import pickle
import os
from typing import Optional

import redis.asyncio as aioredis
import redis
import structlog

log = structlog.get_logger(__name__)

# Redis configuration from environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME", None)
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_TTL = int(os.getenv("REDIS_TTL", "3600"))

# Global Redis clients (initialized lazily)
_redis_client: Optional[redis.Redis] = None
_async_redis_client: Optional[aioredis.Redis] = None


def get_redis_client() -> redis.Redis:
    """Get or create synchronous Redis client."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=False,  # We handle binary data for pickle
        )
        log.info("redis_client_initialized", host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    return _redis_client


async def get_async_redis_client() -> aioredis.Redis:
    """Get or create asynchronous Redis client."""
    global _async_redis_client
    if _async_redis_client is None:
        _async_redis_client = aioredis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            username=REDIS_USERNAME,
            password=REDIS_PASSWORD,
            db=REDIS_DB,
            decode_responses=False,  # We handle binary data for pickle
        )
        log.info("async_redis_client_initialized", host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    return _async_redis_client


def _make_key(prefix: str, args, kwargs, exclude_keys: set[str]) -> str:
    """Generate cache key from function arguments."""
    # Filter out excluded keys from kwargs
    filtered_kwargs = {k: v for k, v in kwargs.items() if k not in exclude_keys}
    raw = json.dumps({"a": args, "k": filtered_kwargs}, sort_keys=True, default=str)
    return prefix + ":" + hashlib.sha256(raw.encode()).hexdigest()


def cached(prefix: str = "", exclude: list[str] | None = None, ttl: int | None = None):
    """Redis-based caching decorator. Works with both sync and async functions.

    Args:
        prefix: Cache key prefix
        exclude: List of parameter names to exclude from cache key (e.g., ['db'])
        ttl: Time-to-live in seconds (defaults to REDIS_TTL from environment)
    """
    exclude_keys = set(exclude or [])
    cache_ttl = ttl if ttl is not None else REDIS_TTL

    def decorator(fn):
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def wrapper(*args, **kwargs):
                key = _make_key(prefix, args, kwargs, exclude_keys)
                client = await get_async_redis_client()

                # Try to get from cache
                try:
                    cached_value = await client.get(key)
                    if cached_value is not None:
                        log.info("cache_hit", prefix=prefix, key=key[:32])
                        return pickle.loads(cached_value)
                except Exception as e:
                    log.warning("cache_get_error", error=str(e), key=key[:32])

                # Cache miss - execute function
                log.info("cache_miss", prefix=prefix, key=key[:32])
                result = await fn(*args, **kwargs)

                # Store in cache
                try:
                    serialized = pickle.dumps(result)
                    await client.set(key, serialized, ex=cache_ttl)
                    log.debug("cache_set", prefix=prefix, key=key[:32], ttl=cache_ttl)
                except Exception as e:
                    log.warning("cache_set_error", error=str(e), key=key[:32])

                return result
        else:
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                key = _make_key(prefix, args, kwargs, exclude_keys)
                client = get_redis_client()

                # Try to get from cache
                try:
                    cached_value = client.get(key)
                    if cached_value is not None:
                        log.info("cache_hit", prefix=prefix, key=key[:32])
                        return pickle.loads(cached_value)
                except Exception as e:
                    log.warning("cache_get_error", error=str(e), key=key[:32])

                # Cache miss - execute function
                log.info("cache_miss", prefix=prefix, key=key[:32])
                result = fn(*args, **kwargs)

                # Store in cache
                try:
                    serialized = pickle.dumps(result)
                    client.set(key, serialized, ex=cache_ttl)
                    log.debug("cache_set", prefix=prefix, key=key[:32], ttl=cache_ttl)
                except Exception as e:
                    log.warning("cache_set_error", error=str(e), key=key[:32])

                return result

        return wrapper

    return decorator


async def invalidate_async(prefix: str = ""):
    """Remove all cache entries matching a prefix (or clear everything) - async version."""
    client = await get_async_redis_client()

    if prefix:
        # Find all keys matching the prefix pattern
        pattern = f"{prefix}:*" if not prefix.endswith(":") else f"{prefix}*"
        cursor = 0
        keys_removed = 0

        while True:
            cursor, keys = await client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                await client.delete(*keys)
                keys_removed += len(keys)
            if cursor == 0:
                break

        log.info("cache_invalidated_async", prefix=prefix, keys_removed=keys_removed)
    else:
        # Clear entire database
        await client.flushdb()
        log.info("cache_cleared_async")


def invalidate(prefix: str = ""):
    """Remove all cache entries matching a prefix (or clear everything) - sync version."""
    client = get_redis_client()

    if prefix:
        # Find all keys matching the prefix pattern
        pattern = f"{prefix}:*" if not prefix.endswith(":") else f"{prefix}*"
        cursor = 0
        keys_removed = 0

        while True:
            cursor, keys = client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                client.delete(*keys)
                keys_removed += len(keys)
            if cursor == 0:
                break

        log.info("cache_invalidated", prefix=prefix, keys_removed=keys_removed)
    else:
        # Clear entire database
        client.flushdb()
        log.info("cache_cleared")


async def check_redis() -> dict:
    """Check Redis connectivity."""
    try:
        client = await get_async_redis_client()
        await client.ping()
        log.debug("redis_health_check_ok")
        return {"status": "ok", "error": None}
    except Exception as e:
        log.error("redis_health_check_error", error=str(e))
        return {"status": "error", "error": str(e)}

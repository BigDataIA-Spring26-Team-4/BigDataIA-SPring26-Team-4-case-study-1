import hashlib
import json
import asyncio
import functools

_cache: dict[str, any] = {}


def _make_key(prefix: str, args, kwargs) -> str:
    raw = json.dumps({"a": args, "k": kwargs}, sort_keys=True, default=str)
    return prefix + hashlib.sha256(raw.encode()).hexdigest()


def cached(prefix: str = ""):
    """In-memory caching decorator. Works with both sync and async functions."""

    def decorator(fn):
        if asyncio.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def wrapper(*args, **kwargs):
                key = _make_key(prefix, args, kwargs)
                if key in _cache:
                    return _cache[key]
                result = await fn(*args, **kwargs)
                _cache[key] = result
                return result
        else:
            @functools.wraps(fn)
            def wrapper(*args, **kwargs):
                key = _make_key(prefix, args, kwargs)
                if key in _cache:
                    return _cache[key]
                result = fn(*args, **kwargs)
                _cache[key] = result
                return result

        return wrapper

    return decorator


def invalidate(prefix: str = ""):
    """Remove all cache entries matching a prefix (or clear everything)."""
    keys = [k for k in _cache if k.startswith(prefix)]
    for k in keys:
        del _cache[k]

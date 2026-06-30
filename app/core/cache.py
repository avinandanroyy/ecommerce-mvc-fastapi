import redis.asyncio as redis
import json
from typing import Any, Optional, Dict, List
from functools import wraps
from datetime import timedelta

from app.core.config import settings


class CacheService:
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self.is_connected = False

    async def connect(self):
        try:
            self.client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                encoding="utf-8",
            )
            await self.client.ping()
            self.is_connected = True
        except Exception:
            self.is_connected = False

    async def disconnect(self):
        if self.client:
            await self.client.close()
            self.is_connected = False

    async def get(self, key: str) -> Optional[Any]:
        if not self.is_connected or not self.client:
            return None
        try:
            value = await self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception:
            return None

    async def set(self, key: str, value: Any, expire: Optional[timedelta] = None) -> bool:
        if not self.is_connected or not self.client:
            return False
        try:
            serialized = json.dumps(value)
            if expire:
                return await self.client.setex(key, int(expire.total_seconds()), serialized)
            return await self.client.set(key, serialized)
        except Exception:
            return False

    async def delete(self, key: str) -> bool:
        if not self.is_connected or not self.client:
            return False
        try:
            await self.client.delete(key)
            return True
        except Exception:
            return False

    async def delete_pattern(self, pattern: str) -> int:
        if not self.is_connected or not self.client:
            return 0
        try:
            keys = await self.client.keys(pattern)
            if keys:
                return await self.client.delete(*keys)
            return 0
        except Exception:
            return 0

    async def exists(self, key: str) -> bool:
        if not self.is_connected or not self.client:
            return False
        try:
            return await self.client.exists(key) > 0
        except Exception:
            return False

    async def get_or_set(self, key: str, factory: callable, expire: Optional[timedelta] = None) -> Any:
        value = await self.get(key)
        if value is None:
            value = await factory()
            await self.set(key, value, expire)
        return value


cache_service = CacheService()


def cached(expire: Optional[timedelta] = None, key_prefix: str = ""):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            if not cache_service.is_connected:
                return await func(*args, **kwargs)
            
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
            
            value = await cache_service.get(cache_key)
            if value is not None:
                return value
            
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, expire)
            return result
        
        return wrapper
    return decorator


def invalidate_cache(pattern: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            result = await func(*args, **kwargs)
            if cache_service.is_connected:
                await cache_service.delete_pattern(pattern)
            return result
        return wrapper
    return decorator

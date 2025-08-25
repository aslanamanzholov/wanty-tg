"""Redis cache for user states and data."""
import json
import logging
from typing import Optional, Dict, Any
from redis.asyncio import Redis

from src.configuration import conf


class RedisCache:
    """Redis cache manager for user states and data."""
    
    def __init__(self, redis_client: Redis):
        """Initialize Redis cache manager."""
        self.redis = redis_client
        self.default_ttl = 3600  # 1 час по умолчанию
    
    async def set_user_offset(self, user_id: int, offset: int, ttl: int = None) -> None:
        """Set user's dream offset."""
        key = f"user_offset:{user_id}"
        await self.redis.setex(key, ttl or self.default_ttl, offset)
    
    async def get_user_offset(self, user_id: int) -> int:
        """Get user's dream offset."""
        key = f"user_offset:{user_id}"
        value = await self.redis.get(key)
        return int(value) if value else 0
    
    async def increment_user_offset(self, user_id: int, ttl: int = None) -> int:
        """Increment user's dream offset."""
        key = f"user_offset:{user_id}"
        offset = await self.redis.incr(key)
        await self.redis.expire(key, ttl or self.default_ttl)
        return offset
    
    async def clear_user_offset(self, user_id: int) -> None:
        """Clear user's dream offset."""
        key = f"user_offset:{user_id}"
        await self.redis.delete(key)
    
    async def set_image_cache(self, image_hash: str, image_data: bytes, ttl: int = 7200) -> None:
        """Cache image data."""
        key = f"image:{image_hash}"
        await self.redis.setex(key, ttl, image_data)
    
    async def get_image_cache(self, image_hash: str) -> Optional[bytes]:
        """Get cached image data."""
        key = f"image:{image_hash}"
        return await self.redis.get(key)
    
    async def clear_expired_images(self) -> None:
        """Clear expired image cache entries."""
        # Redis автоматически очищает по TTL, но можно добавить дополнительную логику
        pass

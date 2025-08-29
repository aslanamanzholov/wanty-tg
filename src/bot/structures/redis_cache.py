"""Redis cache for user states and data."""
import json
import logging
from typing import Optional, Dict, Any
from redis.asyncio import Redis
import time

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
    
    async def reset_user_offset(self, user_id: int) -> None:
        """Reset user's dream offset to 0."""
        key = f"user_offset:{user_id}"
        await self.redis.setex(key, self.default_ttl, 0)
    
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

    async def add_like_notification(self, author_id: int, dream_id: int, liker_info: dict) -> bool:
        """Добавляет уведомление о лайке в очередь для группировки."""
        key = f"like_notifications:{author_id}"
        
        # Получаем существующие уведомления
        existing = await self.redis.get(key)
        if existing:
            notifications = json.loads(existing)
        else:
            notifications = []
        
        # Добавляем новое уведомление
        notification = {
            "dream_id": dream_id,
            "liker_info": liker_info,
            "timestamp": time.time()
        }
        notifications.append(notification)
        
        # Сохраняем обновленный список
        await self.redis.setex(key, 300, json.dumps(notifications))  # TTL 5 минут
        
        return True

    async def get_pending_like_notifications(self, author_id: int) -> list:
        """Получает все ожидающие уведомления о лайках для пользователя."""
        key = f"like_notifications:{author_id}"
        existing = await self.redis.get(key)
        
        if existing:
            notifications = json.loads(existing)
            # Удаляем уведомления старше 5 минут
            current_time = time.time()
            notifications = [n for n in notifications if current_time - n["timestamp"] < 300]
            
            if notifications:
                # Обновляем список без старых уведомлений
                await self.redis.setex(key, 300, json.dumps(notifications))
                return notifications
        
        return []

    async def clear_like_notifications(self, author_id: int) -> bool:
        """Очищает все уведомления о лайках для пользователя."""
        key = f"like_notifications:{author_id}"
        await self.redis.delete(key)
        return True

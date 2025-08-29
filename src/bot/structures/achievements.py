"""Achievement system for Wanty bot."""

from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass


class AchievementType(Enum):
    """Types of achievements."""
    FIRST_DREAM = "first_dream"
    DREAM_MASTER = "dream_master"
    POPULAR_DREAMER = "popular_dreamer"
    ACTIVE_VIEWER = "active_viewer"
    SOCIAL_BUTTERFLY = "social_butterfly"
    WEEKLY_CHAMPION = "weekly_champion"
    CONSISTENT_USER = "consistent_user"
    HELPING_HAND = "helping_hand"


@dataclass
class Achievement:
    """Achievement data structure."""
    id: str
    name: str
    description: str
    emoji: str
    requirement: str
    points: int
    type: AchievementType


class AchievementSystem:
    """Manages user achievements and progress."""
    
    def __init__(self):
        """Initialize achievement system."""
        self.achievements = self._initialize_achievements()
    
    def _initialize_achievements(self) -> Dict[str, Achievement]:
        """Initialize all available achievements."""
        return {
            "first_dream": Achievement(
                id="first_dream",
                name="Первый шаг",
                description="Создал свое первое желание",
                emoji="🌟",
                requirement="Создать 1 желание",
                points=10,
                type=AchievementType.FIRST_DREAM
            ),
            "dream_master": Achievement(
                id="dream_master",
                name="Мастер желаний",
                description="Создал 10 желаний",
                emoji="👑",
                requirement="Создать 10 желаний",
                points=50,
                type=AchievementType.DREAM_MASTER
            ),
            "popular_dreamer": Achievement(
                id="popular_dreamer",
                name="Популярный мечтатель",
                description="Получил 25 лайков на свои желания",
                emoji="🔥",
                requirement="Получить 25 лайков",
                points=75,
                type=AchievementType.POPULAR_DREAMER
            ),
            "active_viewer": Achievement(
                id="active_viewer",
                name="Активный зритель",
                description="Просмотрел 50 желаний",
                emoji="👀",
                requirement="Просмотреть 50 желаний",
                points=30,
                type=AchievementType.ACTIVE_VIEWER
            ),
            "social_butterfly": Achievement(
                id="social_butterfly",
                name="Общительная бабочка",
                description="Поставил 100 лайков",
                emoji="🦋",
                requirement="Поставить 100 лайков",
                points=60,
                type=AchievementType.SOCIAL_BUTTERFLY
            ),
            "weekly_champion": Achievement(
                id="weekly_champion",
                name="Чемпион недели",
                description="Был самым активным пользователем недели",
                emoji="🏆",
                requirement="Стать лучшим за неделю",
                points=100,
                type=AchievementType.WEEKLY_CHAMPION
            ),
            "consistent_user": Achievement(
                id="consistent_user",
                name="Постоянный пользователь",
                description="Использовал бота 7 дней подряд",
                emoji="📅",
                requirement="7 дней активности",
                points=40,
                type=AchievementType.CONSISTENT_USER
            ),
            "helping_hand": Achievement(
                id="helping_hand",
                name="Помощник",
                description="Помог 5 пользователям найти единомышленников",
                emoji="🤝",
                requirement="Помочь 5 пользователям",
                points=80,
                type=AchievementType.HELPING_HAND
            )
        }
    
    def get_achievement(self, achievement_id: str) -> Optional[Achievement]:
        """Get achievement by ID."""
        return self.achievements.get(achievement_id)
    
    def get_all_achievements(self) -> List[Achievement]:
        """Get all available achievements."""
        return list(self.achievements.values())
    
    def get_achievements_by_type(self, achievement_type: AchievementType) -> List[Achievement]:
        """Get achievements by type."""
        return [a for a in self.achievements.values() if a.type == achievement_type]
    
    def check_achievement_unlock(self, user_stats: Dict, achievement_id: str) -> bool:
        """Check if user unlocked specific achievement."""
        achievement = self.get_achievement(achievement_id)
        if not achievement:
            return False
        
        if achievement_id == "first_dream":
            return user_stats.get("total_dreams", 0) >= 1
        elif achievement_id == "dream_master":
            return user_stats.get("total_dreams", 0) >= 10
        elif achievement_id == "popular_dreamer":
            return user_stats.get("total_likes_received", 0) >= 25
        elif achievement_id == "active_viewer":
            return user_stats.get("total_dreams_viewed", 0) >= 50
        elif achievement_id == "social_butterfly":
            return user_stats.get("total_likes_given", 0) >= 100
        elif achievement_id == "consistent_user":
            return user_stats.get("consecutive_days", 0) >= 7
        elif achievement_id == "helping_hand":
            return user_stats.get("users_helped", 0) >= 5
        
        return False
    
    def get_user_progress(self, user_stats: Dict) -> Dict[str, Dict]:
        """Get user's progress towards all achievements."""
        progress = {}
        
        for achievement_id, achievement in self.achievements.items():
            current_value = self._get_current_value(user_stats, achievement_id)
            required_value = self._get_required_value(achievement_id)
            is_unlocked = self.check_achievement_unlock(user_stats, achievement_id)
            
            progress[achievement_id] = {
                "achievement": achievement,
                "current_value": current_value,
                "required_value": required_value,
                "is_unlocked": is_unlocked,
                "progress_percentage": min(100, (current_value / required_value * 100)) if required_value > 0 else 100
            }
        
        return progress
    
    def _get_current_value(self, user_stats: Dict, achievement_id: str) -> int:
        """Get current value for achievement progress."""
        if achievement_id == "first_dream":
            return user_stats.get("total_dreams", 0)
        elif achievement_id == "dream_master":
            return user_stats.get("total_dreams", 0)
        elif achievement_id == "popular_dreamer":
            return user_stats.get("total_likes_received", 0)
        elif achievement_id == "active_viewer":
            return user_stats.get("total_dreams_viewed", 0)
        elif achievement_id == "social_butterfly":
            return user_stats.get("total_likes_given", 0)
        elif achievement_id == "consistent_user":
            return user_stats.get("consecutive_days", 0)
        elif achievement_id == "helping_hand":
            return user_stats.get("users_helped", 0)
        
        return 0
    
    def _get_required_value(self, achievement_id: str) -> int:
        """Get required value for achievement."""
        if achievement_id == "first_dream":
            return 1
        elif achievement_id == "dream_master":
            return 10
        elif achievement_id == "popular_dreamer":
            return 25
        elif achievement_id == "active_viewer":
            return 50
        elif achievement_id == "social_butterfly":
            return 100
        elif achievement_id == "consistent_user":
            return 7
        elif achievement_id == "helping_hand":
            return 5
        
        return 0


# Глобальный экземпляр системы достижений
achievement_system = AchievementSystem()

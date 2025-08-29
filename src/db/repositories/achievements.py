"""Achievements repository for Wanty bot."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from src.db.models.achievements import UserAchievement, UserProgress
from src.db.models.user import User
from src.db.repositories.abstract import Repository


class AchievementsRepository(Repository[UserAchievement]):
    """Repository for user achievements."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=UserAchievement, session=session)
    
    async def get_user_achievements(self, user_id: int) -> List[UserAchievement]:
        """Get all achievements for a user."""
        query = select(UserAchievement).where(UserAchievement.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def unlock_achievement(self, user_id: int, achievement_id: str, points: int) -> UserAchievement:
        """Unlock achievement for user."""
        # Проверяем, существует ли пользователь
        user_query = select(User).where(User.user_id == user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} does not exist")
        
        achievement = UserAchievement(
            user_id=user_id,
            achievement_id=achievement_id,
            points_earned=points
        )
        self.session.add(achievement)
        await self.session.commit()
        return achievement
    
    async def is_achievement_unlocked(self, user_id: int, achievement_id: str) -> bool:
        """Check if user has unlocked specific achievement."""
        query = select(UserAchievement).where(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None


class ProgressRepository(Repository[UserProgress]):
    """Repository for user progress."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=UserProgress, session=session)
    
    async def get_user_progress(self, user_id: int) -> Optional[UserProgress]:
        """Get user progress."""
        query = select(UserProgress).where(UserProgress.user_id == user_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def create_user_progress(self, user_id: int) -> UserProgress:
        """Create progress record for new user."""
        # Проверяем, существует ли пользователь
        user_query = select(User).where(User.user_id == user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} does not exist")
        
        progress = UserProgress(user_id=user_id)
        self.session.add(progress)
        await self.session.commit()
        return progress
    
    async def increment_dreams(self, user_id: int, points: int = 15) -> UserProgress:
        """Increment user's dream count and points."""
        # Проверяем, существует ли пользователь
        user_query = select(User).where(User.user_id == user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} does not exist")
        
        progress = await self.get_user_progress(user_id)
        if not progress:
            progress = await self.create_user_progress(user_id)
        
        progress.total_dreams += 1
        progress.total_points += points
        await self.session.commit()
        return progress
    
    async def increment_likes_received(self, user_id: int, points: int = 5) -> UserProgress:
        """Increment user's received likes count and points."""
        # Проверяем, существует ли пользователь
        user_query = select(User).where(User.user_id == user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} does not exist")
        
        progress = await self.get_user_progress(user_id)
        if not progress:
            progress = await self.create_user_progress(user_id)
        
        progress.total_likes_received += 1
        progress.total_points += points
        await self.session.commit()
        return progress
    
    async def increment_dreams_viewed(self, user_id: int, points: int = 1) -> UserProgress:
        """Increment user's viewed dreams count and points."""
        # Проверяем, существует ли пользователь
        user_query = select(User).where(User.user_id == user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} does not exist")
        
        progress = await self.get_user_progress(user_id)
        if not progress:
            progress = await self.create_user_progress(user_id)
        
        progress.total_dreams_viewed += 1
        progress.total_points += points
        await self.session.commit()
        return progress
    
    async def increment_likes_given(self, user_id: int, points: int = 2) -> UserProgress:
        """Increment user's given likes count and points."""
        # Проверяем, существует ли пользователь
        user_query = select(User).where(User.user_id == user_id)
        user_result = await self.session.execute(user_query)
        user = user_result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} does not exist")
        
        progress = await self.get_user_progress(user_id)
        if not progress:
            progress = await self.create_user_progress(user_id)
        
        progress.total_likes_given += 1
        progress.total_points += points
        await self.session.commit()
        return progress

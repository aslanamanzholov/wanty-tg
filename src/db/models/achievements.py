"""Achievement models for Wanty bot."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.models.base import Base


class UserAchievement(Base):
    """User achievement model."""
    __tablename__ = "user_achievements"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False)  # Changed from Integer to BigInteger
    achievement_id = Column(String(50), nullable=False)  # ID достижения из системы
    unlocked_at = Column(DateTime(timezone=True), server_default=func.now())
    points_earned = Column(Integer, default=0)
    



class UserProgress(Base):
    """User progress tracking model."""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.user_id"), nullable=False, unique=True)  # Changed from Integer to BigInteger
    
    # Статистика активности
    total_dreams = Column(Integer, default=0)
    total_likes_received = Column(Integer, default=0)
    total_dreams_viewed = Column(Integer, default=0)
    total_likes_given = Column(Integer, default=0)
    consecutive_days = Column(Integer, default=0)
    users_helped = Column(Integer, default=0)
    
    # Очки и достижения
    total_points = Column(Integer, default=0)
    last_activity_date = Column(DateTime(timezone=True), server_default=func.now())
    


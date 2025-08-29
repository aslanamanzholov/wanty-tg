"""Achievements middleware for gamification system."""
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from src.bot.structures.data_structure import TransferData
from src.bot.structures.achievements import GamificationManager


class AchievementsMiddleware(BaseMiddleware):
    """This middleware manages achievements and gamification."""

    def __init__(self):
        """Initialize achievements middleware."""
        super().__init__()
        self.gamification = GamificationManager()

    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: TransferData,
    ) -> Any:
        """Add gamification manager to data."""
        data['gamification'] = self.gamification
        return await handler(event, data)

"""Dream repository file."""
import logging
from collections.abc import Sequence
from typing import Any

from sqlalchemy import select, ScalarResult, delete, CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Base, Dream, User
from .abstract import Repository


class DreamRepo(Repository[Dream]):
    """User repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository as for all users or only for one user."""
        super().__init__(type_model=Dream, session=session)

    async def new(
            self,
            user_id: int,
            username: str | None = None,
            image: bytes | None = None,
            name: str | None = None,
            description: str | None = None,
    ) -> None:
        """Insert a new user into the database.

        :param user_id: Telegram user id
        :param username: Telegram username
        :param image: Image of Dream
        :param name: Name of Dream
        :param description: Description of Dream
        """
        await self.session.merge(
            Dream(
                user_id=user_id,
                username=username,
                image=image,
                name=name,
                description=description
            )
        )
        await self.session.commit()

    async def get_dream(self, user_id, offset, limit: int = 1):
        """Get dream"""
        statement = select(self.type_model).where(Dream.user_id != user_id).offset(offset).limit(limit)

        return (await self.session.scalars(statement)).first()

    async def get_elements_count_of_dream(self, user_id) -> int:
        """Get dream"""
        statement = select(self.type_model).where(Dream.user_id != user_id)

        return (await self.session.scalars(statement)).all().count(0)

    async def get_dreams_of_user(self, user_id: int, limit: int = 100) -> Sequence[Base]:
        """Get user dreams by id."""
        statement = select(self.type_model).where(Dream.user_id == user_id).limit(limit)

        return (await self.session.scalars(statement)).all()

    async def get_dream_by_id(self, dream_id: int):
        """Get user dreams by id."""
        statement = select(self.type_model).where(Dream.id == dream_id)

        return (await self.session.scalars(statement)).first()

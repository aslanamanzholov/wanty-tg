"""Dream repository file."""
import logging
from collections.abc import Sequence

from sqlalchemy import select, ScalarResult
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
            name: str | None = None,
            description: str | None = None,
    ) -> None:
        """Insert a new user into the database.

        :param user_id: Telegram user id
        :param name: Name of Dream
        :param description: Description of Dream
        """
        await self.session.merge(
            Dream(
                user_id=user_id,
                name=name,
                description=description
            )
        )
        await self.session.commit()

    async def get_list_of_dreams(self, user_id, limit: int = 1) -> Sequence[Base]:
        """Get user role by id."""
        statement = select(self.type_model).where(Dream.user_id != user_id).limit(limit)

        return (await self.session.scalars(statement)).all()

    async def get_next_obj_of_dream(self, user_id, offset: int = 1, limit: int = 1) -> Sequence[Base]:
        """Get dream"""
        statement = select(self.type_model).where(Dream.user_id != user_id).limit(limit).offset(offset)

        return (await self.session.scalars(statement)).all()

    async def get_elements_count_of_dream(self, user_id, offset: int = 0, limit: int = 1) -> int:
        """Get dream"""
        statement = select(self.type_model).where(Dream.user_id != user_id)

        return (await self.session.scalars(statement)).all().count(0)

    async def get_dreams_of_user(self, user_id: int, limit: int = 100) -> Sequence[Base]:
        """Get user dreams by id."""
        statement = select(self.type_model).filter(Dream.user_id == user_id).limit(limit)

        return (await self.session.scalars(statement)).all()

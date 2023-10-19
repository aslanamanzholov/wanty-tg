"""User repository file."""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.structures.role import Role

from ..models import Base, User
from .abstract import Repository


class UserRepo(Repository[User]):
    """User repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository as for all users or only for one user."""
        super().__init__(type_model=User, session=session)

    async def new(
        self,
        user_id: int,
        user_name: str | None = None,
        age: str | None = None,
        gender: str | None = None,
        country: str | None = None,
        role: Optional[Role] = Role.USER,
        user_chat: type[Base] = None,
    ) -> None:
        """Insert a new user into the database.

        :param user_id: Telegram user id
        :param user_name: Telegram username
        :param age: Telegram profile first name
        :param gender: Telegram profile second name
        :param country: Telegram profile language code
        :param role: User's role
        :param user_chat: Telegram chat with user.
        """
        await self.session.merge(
            User(
                user_id=user_id,
                user_name=user_name,
                age=age,
                gender=gender,
                country=country,
                role=role,
                user_chat=user_chat,
            )
        )

    async def get_role(self, user_id: int) -> Role:
        """Get user role by id."""
        return await self.session.scalar(
            select(User.role).where(User.user_id == user_id).limit(1)
        )

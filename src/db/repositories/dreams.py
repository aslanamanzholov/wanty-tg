"""Dream repository file."""
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Base, Dream
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

    async def get_list_of_dreams(self, limit: int = 1) -> Sequence[Base]:
        """Get user role by id."""
        statement = select(self.type_model).limit(limit)

        return (await self.session.scalars(statement)).all()

    async def get_next_obj_of_dream(self, limit: int = 1, offset: int = 1) -> Sequence[Base]:
        """Get user role by id."""
        statement = select(self.type_model).limit(limit).offset(offset)

        return (await self.session.scalars(statement)).all()

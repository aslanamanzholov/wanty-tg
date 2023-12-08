"""Dream repository file."""
from collections.abc import Sequence

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .abstract import Repository
from src.db.models import Base
from src.db.models.dreams import Dream, DreamLikedRecord


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
        statement = (
            select(self.type_model)
            .where(Dream.user_id != user_id)
            .offset(offset)
            .limit(limit)
        )

        return (await self.session.execute(statement.order_by(func.random()))).scalars().first()

    async def get_elements_count_of_dream(self, user_id) -> int:
        """Get dream"""
        statement = select(self.type_model).where(Dream.user_id != user_id)

        return (await self.session.scalars(statement)).all().count(0)

    async def get_dreams_of_user(self, user_id: int, limit: int = 100) -> Sequence[Base]:
        """Get user dreams by id."""
        statement = select(self.type_model).where(Dream.user_id == user_id).limit(limit)

        return (await self.session.scalars(statement)).all()

    async def get_dream_by_id(self, dream_id: int):
        """Get user dream by id."""
        statement = select(self.type_model).where(Dream.id == int(dream_id))

        return (await self.session.scalars(statement)).first()


class DreamLikedRecordRepo(Repository[DreamLikedRecord]):
    """Dream Liked Record repository for CRUD and other SQL queries."""

    def __init__(self, session: AsyncSession):
        """Initialize user repository as for all users or only for one user."""
        super().__init__(type_model=DreamLikedRecord, session=session)

    async def new(
            self,
            author_user_id: int,
            liked_user_id: int,
            author_username: str | None = None,
            liked_username: str | None = None,
            dream_name: str | None = None,
            type_feedback: str | None = None,
    ) -> None:
        """Insert a new user into the database.

        :param author_user_id: Author user id
        :param author_username: Author username
        :param liked_user_id: Liked User id of Dream
        :param liked_username: Liked Username of Dream
        :param dream_name: Name of Dream
        :param type_feedback: Type Feedback of Dream
        """
        await self.session.merge(
            DreamLikedRecord(
                author_username_id=author_username,
                liked_username_id=liked_username,
                dream_name=dream_name,
                type_feedback=type_feedback
            )
        )
        await self.session.commit()

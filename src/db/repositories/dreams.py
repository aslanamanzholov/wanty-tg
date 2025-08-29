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
        category: str | None = None,
    ) -> None:
        """Insert a new dream into the database."""
        new_dream = Dream(
            user_id=user_id,
            username=username,
            image=image,
            name=name,
            description=description,
            category=category,
        )
        self.session.add(new_dream)
        await self.session.commit()

    async def get_dream(self, user_id, offset, limit: int = 1):
        """Get a dream."""
        statement = (
            select(self.type_model)
            .where(Dream.user_id != user_id)
            .order_by(Dream.id)  # Добавляем сортировку для стабильного порядка
            .offset(offset)
            .limit(limit)
        )

        return await self.session.scalar(statement)

    async def get_dream_excluding_user(self, user_id, offset, limit: int = 1):
        """Get a dream excluding the current user's dreams."""
        return await self.get_dream(user_id, offset, limit)

    async def get_elements_count_of_dream(self, user_id) -> int:
        """Получение количества желаний."""
        statement = select(func.count()).where(Dream.user_id != user_id)
        return await self.session.scalar(statement)

    async def get_dreams_of_user(self, user_id: int, limit: int = 100) -> Sequence[Base]:
        """Получение желаний пользователя по его ID."""
        statement = select(self.type_model).where(Dream.user_id == user_id).limit(limit)
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_dream_by_id(self, dream_id: int):
        """Get user dream by id."""
        statement = select(self.type_model).where(Dream.id == int(dream_id))
        return await self.session.scalar(statement)


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
        """Insert a new record into the database."""
        await self.session.merge(
            DreamLikedRecord(
                author_username_id=author_username,
                liked_username_id=liked_username,
                dream_name=dream_name,
                type_feedback=type_feedback
            )
        )
        await self.session.commit()

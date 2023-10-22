"""Database class with all-in-one features."""

from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine as _create_async_engine

from src.configuration import conf

from .repositories import UserRepo, DreamRepo


def create_async_engine(url: URL | str) -> AsyncEngine:
    """Create async engine with given URL.

    :param url: URL to connect
    :return: AsyncEngine
    """
    return _create_async_engine(url=url, echo=conf.debug, pool_pre_ping=True)


class Database:
    """Database class.

    is the highest abstraction level of database and
    can be used in the handlers or any others bot-side functions.
    """

    user: UserRepo
    """ User repository """
    dream: DreamRepo
    """ Dream repository """

    session: AsyncSession

    def __init__(
        self,
        session: AsyncSession,
        user: UserRepo = None,
        dream: DreamRepo = None,
    ):
        """Initialize Database class.

        :param session: AsyncSession to use
        :param user: (Optional) User repository
        """
        self.session = session
        self.user = user or UserRepo(session=session)
        self.dream = dream or DreamRepo(session=session)

"""User model file."""
import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base
from src.bot.structures.role import Role


class User(Base):
    """User model."""

    user_id: Mapped[int] = mapped_column(
        sa.BigInteger, unique=True, nullable=False
    )
    """ Telegram user id """
    user_name: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    name: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    age: Mapped[int] = mapped_column(
        sa.SmallInteger, unique=False, nullable=True
    )
    gender: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    country: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    role: Mapped[Role] = mapped_column(sa.Enum(Role), default=Role.USER)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

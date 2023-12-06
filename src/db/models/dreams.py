"""Dream model file."""
import datetime

import sqlalchemy as sa
from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Dream(Base):
    """Dream model."""

    """ Telegram from user id """
    user_id: Mapped[int] = mapped_column(
        sa.BigInteger, unique=False, nullable=False
    )
    """ Telegram from user name """
    username: Mapped[int] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    image = mapped_column(
        sa.LargeBinary, nullable=True
    )
    name: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    description: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())


class DreamLikedRecord(Base):
    """DreamLikedRecordRepo model."""

    author_username_id: Mapped[int] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    liked_username_id: Mapped[int] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    dream_name: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    type_feedback: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at = mapped_column(DateTime(timezone=True), onupdate=func.now())

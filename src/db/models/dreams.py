"""Dream model file."""
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Dream(Base):
    """Dream model."""

    user_id: Mapped[int] = mapped_column(
        sa.BigInteger, unique=False, nullable=False
    )
    """ Telegram user id """
    name: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )
    description: Mapped[str] = mapped_column(
        sa.Text, unique=False, nullable=True
    )

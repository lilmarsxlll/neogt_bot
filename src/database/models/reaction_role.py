from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models.base import Base


class ReactionRole(Base):
    """ORM модель для связи между эмоджи-реакциями и Discord ролями.

    Attributes:
        id: Уникальный идентификатор записи.
        guild_id: ID Discord-сервера.
        emoji: Эмоджи (Unicode или Discord custom формат).
        role_id: ID Discord-роли, выдаваемой при реакции.
        created_at: Дата и время создания записи.
    """

    __tablename__ = "reaction_roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    guild_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    emoji: Mapped[str] = mapped_column(String(100), nullable=False)
    role_id: Mapped[int] = mapped_column(BigInteger, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))

    __table_args__ = (UniqueConstraint("guild_id", "emoji", name="uq_guild_emoji"),)

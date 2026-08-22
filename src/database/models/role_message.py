from datetime import UTC, datetime

from sqlalchemy import BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from src.database.models.base import Base


class RoleMessage(Base):
    """ORM модель для сообщений с реакциями для выдачи ролей.

    Attributes:
        message_id: ID Discord-сообщения (primary key).
        channel_id: ID Discord-канала с сообщением.
        guild_id: ID Discord-сервера (уникальный, один на сервер).
        created_at: Дата и время создания записи.
    """

    __tablename__ = "role_messages"

    message_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    guild_id: Mapped[int] = mapped_column(
        BigInteger, nullable=False, unique=True, index=True
    )

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))

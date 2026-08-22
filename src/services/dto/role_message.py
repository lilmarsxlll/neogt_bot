from pydantic import BaseModel, Field


class RoleMessageDTO(BaseModel):
    """DTO для отслеживаемого сообщения с реакциями.

    Attributes:
        message_id: ID Discord-сообщения.
        channel_id: ID канала, где находится сообщение.
        guild_id: ID Discord-сервера.
    """

    message_id: int = Field(..., gt=0)
    channel_id: int = Field(..., gt=0)
    guild_id: int = Field(..., gt=0)


class SetupMessageRequest(BaseModel):
    """DTO для запроса настройки сообщения с реакциями.

    Attributes:
        guild_id: ID Discord-сервера.
        channel_id: ID канала для создания/обновления сообщения.
        force_recreate: Принудительно пересоздать сообщение (по умолчанию False).
    """

    guild_id: int = Field(..., gt=0)
    channel_id: int = Field(..., gt=0)
    force_recreate: bool = Field(default=False)


class SetupMessageResult(BaseModel):
    """DTO с результатом настройки сообщения с реакциями.

    Attributes:
        message: DTO созданного/обновлённого сообщения.
        message_url: Прямая ссылка на сообщение.
        reactions_added: Список добавленных эмоджи-реакций.
        reactions_removed: Список удалённых эмоджи-реакций.
        was_created: True если сообщение было создано, False если обновлено.
    """

    message: RoleMessageDTO
    message_url: str
    reactions_added: list[str] = Field(default_factory=list)
    reactions_removed: list[str] = Field(default_factory=list)
    was_created: bool = False

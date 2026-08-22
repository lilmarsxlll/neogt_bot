from pydantic import BaseModel


class PrivateRoomResult(BaseModel):
    """DTO с результатом создания приватной голосовой комнаты.

    Attributes:
        channel_id: ID созданного голосового канала.
        channel_name: Название канала.
        channel_mention: Упоминание канала для Discord.
        affected_users: Количество пользователей, добавленных в комнату.
    """

    channel_id: int
    channel_name: str
    channel_mention: str
    affected_users: int


class MoveMembersResult(BaseModel):
    """DTO с результатом перемещения участников в голосовой канал.

    Attributes:
        affected_users: Количество перемещённых пользователей.
        channel_id: ID целевого голосового канала.
        channel_name: Название канала.
    """

    affected_users: int
    channel_id: int
    channel_name: str


class TemporaryRoomAccessResult(BaseModel):
    """DTO с результатом предоставления доступа к временной комнате.

    Attributes:
        member_id: ID участника Discord.
        member_name: Имя участника.
        channel_id: ID голосового канала.
        channel_name: Название канала.
        was_granted: True если доступ был предоставлен, False если уже был.
    """

    member_id: int
    member_name: str
    channel_id: int
    channel_name: str
    was_granted: bool


class ChannelCleanupResult(BaseModel):
    """DTO с результатом удаления одного пустого временного канала.

    Attributes:
        channel_id: ID удалённого канала.
        channel_name: Название удалённого канала.
    """

    channel_id: int
    channel_name: str


class ChannelsCleanupResult(BaseModel):
    """DTO с результатом массового удаления пустых временных каналов.

    Attributes:
        deleted_count: Количество удалённых каналов.
        deleted_channels: Список названий удалённых каналов.
        error_count: Количество ошибок при удалении каналов.
    """

    deleted_count: int
    deleted_channels: list[str] = []
    error_count: int = 0

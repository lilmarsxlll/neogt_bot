from datetime import datetime
from typing import Literal

from pydantic import BaseModel, computed_field


class MoveAction(BaseModel):
    """DTO перемещения пользователя для /blame команды.

    Attributes:
        action_type: Тип действия.
        user_mention: Mention пользователя, совершившего перемещение.
        channel_mention: Mention целевого голосового канала.
        move_count: Количество перемещённых пользователей.
        created_at: Время совершения перемещения.
    """

    action_type: Literal["move"] = "move"
    user_mention: str
    channel_mention: str
    move_count: int
    created_at: datetime

    @property
    def user_message(self) -> str:
        return f"{self.user_mention} переместил {self.move_count} гузлини в {self.channel_mention}"


class MuteAction(BaseModel):
    """DTO мута пользователя для /blame команды.

    Attributes:
        action_type: Тип действия.
        user_mention: Mention пользователя, применившего мут.
        target_mention: Mention замученного пользователя.
        created_at: Время применения мута.
    """

    action_type: Literal["mute"] = "mute"
    user_mention: str
    target_mention: str
    created_at: datetime

    @property
    def user_message(self) -> str:
        return f"{self.user_mention} офнул микро {self.target_mention}"


class DeafenAction(BaseModel):
    """DTO отключения звука пользователя для /blame команды.

    Attributes:
        action_type: Тип действия.
        user_mention: Mention пользователя, отключившего звук.
        target_mention: Mention пользователя, которому отключили звук.
        created_at: Время отключения звука.
    """

    action_type: Literal["deafen"] = "deafen"
    user_mention: str
    target_mention: str
    created_at: datetime

    @property
    def user_message(self) -> str:
        return f"{self.user_mention} офнул звук {self.target_mention}"


Action = MoveAction | MuteAction | DeafenAction


class BlameResult(BaseModel):
    """DTO с результатом выполнения команды /blame.

    Attributes:
        actions: Список найденных действий всех типов.
    """

    actions: list[Action]

    @computed_field
    @property
    def count(self) -> int:
        return len(self.actions)

    @property
    def targeted_actions(self) -> list[MuteAction | DeafenAction]:
        """Целевые действия (мут/оглушение конкретного пользователя)."""
        return [
            action
            for action in self.actions
            if isinstance(action, MuteAction | DeafenAction)
        ]

    @property
    def global_actions(self) -> list[MoveAction]:
        """Общие действия (перемещения)."""
        return [action for action in self.actions if isinstance(action, MoveAction)]

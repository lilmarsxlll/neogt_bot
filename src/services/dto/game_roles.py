from pydantic import BaseModel


class GameRoleResult(BaseModel):
    """DTO с результатом операции над игровой ролью.

    Attributes:
        role_name: Название роли.
        role_mention: Упоминание роли для Discord.
        role_id: ID роли.
        affected_users: Количество затронутых пользователей (для удаления).
    """

    role_name: str
    role_mention: str
    role_id: int
    affected_users: int = 0


class RoleApplyResult(BaseModel):
    """DTO с результатом применения/удаления роли участнику.

    Attributes:
        member_id: ID участника Discord.
        member_name: Имя участника.
        role_id: ID роли.
        role_name: Название роли.
        action: Действие (add/remove).
    """

    member_id: int
    member_name: str
    role_id: int
    role_name: str
    action: str

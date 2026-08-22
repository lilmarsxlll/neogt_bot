from pydantic import BaseModel, Field, field_validator


class ReactionRoleDTO(BaseModel):
    """DTO для связи реакция-роль.

    Attributes:
        id: ID записи в базе данных (опционально при создании).
        guild_id: ID Discord-сервера.
        emoji: Эмоджи (Unicode или custom Discord формата <:name:id>).
        role_id: ID Discord-роли.
    """

    id: int | None = None
    guild_id: int = Field(..., gt=0)
    emoji: str = Field(..., min_length=1, max_length=100)
    role_id: int = Field(..., gt=0)

    @field_validator("emoji")
    @classmethod
    def validate_emoji_format(cls, v: str) -> str:
        """Валидирует формат эмоджи.

        Args:
            v: Строка с эмоджи для валидации.

        Returns:
            Провалидированная строка эмоджи.

        Raises:
            ValueError: Если эмоджи пустой или имеет невалидный custom формат.
        """
        if not v:
            raise ValueError("Emoji cannot be empty")

        if (
            v.startswith("<")
            and v.endswith(">")
            and not (v.startswith("<:") or v.startswith("<a:"))
        ):
            raise ValueError("Invalid custom emoji format")

        return v

    model_config = {
        "frozen": False,
        "str_strip_whitespace": True,
    }


class ReactionRoleListDTO(BaseModel):
    """DTO для списка связей реакция-роль.

    Attributes:
        guild_id: ID Discord-сервера.
        mappings: Список связей реакция-роль.
        total_count: Общее количество связей.
    """

    guild_id: int
    mappings: list[ReactionRoleDTO]
    total_count: int = Field(ge=0)

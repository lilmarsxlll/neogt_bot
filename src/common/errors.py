from dataclasses import dataclass
from enum import Enum


class ErrorCode(str, Enum):
    """Коды ошибок приложения."""

    # Discord API Errors
    DISCORD_FORBIDDEN = "discord_forbidden"
    DISCORD_NOT_FOUND = "discord_not_found"
    DISCORD_HTTP_ERROR = "discord_http_error"

    # Voice Channel Errors
    GUILD_NOT_FOUND = "guild_not_found"
    VOICE_CHANNEL_NOT_FOUND = "voice_channel_not_found"
    VOICE_CHANNEL_CREATE_FAILED = "voice_channel_create_failed"
    INVALID_VOICE_CHANNEL = "invalid_voice_channel"
    CATEGORY_NOT_FOUND = "category_not_found"

    # Role Errors
    ROLE_ALREADY_EXISTS = "role_already_exists"
    ROLE_NOT_FOUND = "role_not_found"
    ROLE_CREATE_FAILED = "role_create_failed"
    ROLE_DELETE_FAILED = "role_delete_failed"
    INVALID_ROLE_PREFIX = "invalid_role_prefix"

    # Reaction Role Errors
    NO_REACTION_ROLES = "no_reaction_roles"
    REACTION_ROLE_NOT_FOUND = "reaction_role_not_found"
    INVALID_EMOJI = "invalid_emoji"

    # Member Errors
    MEMBER_NOT_FOUND = "member_not_found"
    MEMBER_NOT_IN_VOICE = "member_not_in_voice"

    # GPT Errors
    GPT_GENERATION_FAILED = "gpt_generation_failed"

    # Generic Errors
    INVALID_INPUT = "invalid_input"
    UNKNOWN_ERROR = "unknown_error"


@dataclass(frozen=True)
class Error:
    """Структурированная ошибка приложения.

    Attributes:
        code: Код ошибки.
        message: Сообщение об ошибке.
        details: Дополнительные детали ошибки.
    """

    code: ErrorCode
    message: str
    details: dict | None = None

    def __str__(self) -> str:
        if self.details:
            return f"[{self.code.value}] {self.message} | {self.details}"
        return f"[{self.code.value}] {self.message}"


ERROR_MESSAGES = {
    ErrorCode.DISCORD_FORBIDDEN: "У бота нет прав для выполнения этой операции",
    ErrorCode.DISCORD_NOT_FOUND: "Объект не найден",
    ErrorCode.DISCORD_HTTP_ERROR: "Ошибка Discord API",
    ErrorCode.GUILD_NOT_FOUND: "Не найден дискорд сервер",
    ErrorCode.VOICE_CHANNEL_NOT_FOUND: "Не найден голосовой канал",
    ErrorCode.VOICE_CHANNEL_CREATE_FAILED: "Не удалось создать голосовой канал",
    ErrorCode.INVALID_VOICE_CHANNEL: "Указанный канал не является голосовым",
    ErrorCode.CATEGORY_NOT_FOUND: "Не найдена категория каналов",
    ErrorCode.ROLE_ALREADY_EXISTS: "Роль уже существует",
    ErrorCode.ROLE_NOT_FOUND: "Роль не найдена",
    ErrorCode.ROLE_CREATE_FAILED: "Не удалось создать роль",
    ErrorCode.ROLE_DELETE_FAILED: "Не удалось удалить роль",
    ErrorCode.INVALID_ROLE_PREFIX: "Неверный префикс роли",
    ErrorCode.NO_REACTION_ROLES: "Нет настроенных ролей для реакций",
    ErrorCode.REACTION_ROLE_NOT_FOUND: "Роль для реакции не найдена",
    ErrorCode.INVALID_EMOJI: "Неверный формат emoji",
    ErrorCode.MEMBER_NOT_FOUND: "Пользователь не найден",
    ErrorCode.MEMBER_NOT_IN_VOICE: "Пользователь не находится в голосовом канале",
    ErrorCode.GPT_GENERATION_FAILED: "Ошибка генерации GPT",
    ErrorCode.INVALID_INPUT: "Неверные входные данные",
    ErrorCode.UNKNOWN_ERROR: "Неизвестная ошибка",
}


def create_error(
    code: ErrorCode, custom_message: str | None = None, **details
) -> Error:
    """Создаёт Error объект с сообщением по умолчанию для кода.

    Args:
        code: Код ошибки.
        custom_message: Кастомное сообщение (опционально).
        **details: Дополнительные детали ошибки.

    Returns:
        Error объект.
    """
    message = custom_message or ERROR_MESSAGES.get(code, "Произошла ошибка")
    return Error(code=code, message=message, details=details or None)

import discord

from src.common.errors import Error, ErrorCode, create_error
from src.config.logging_config import get_logger

logger = get_logger(__name__)


def handle_discord_exception(e: Exception) -> Error:
    """Преобразует Discord exceptions в структурированные Error объекты.

    Args:
        e: Discord исключение для обработки.

    Returns:
        Error объект с соответствующим кодом ошибки.
    """
    if isinstance(e, discord.Forbidden):
        logger.error(f"Discord Forbidden error: {e}")
        return create_error(
            ErrorCode.DISCORD_FORBIDDEN,
            details={"exception": str(e), "status": 403},
        )

    if isinstance(e, discord.NotFound):
        logger.error(f"Discord NotFound error: {e}")
        return create_error(
            ErrorCode.DISCORD_NOT_FOUND,
            details={"exception": str(e), "status": 404},
        )

    if isinstance(e, discord.HTTPException):
        logger.error(f"Discord HTTPException: {e}", exc_info=True)
        return create_error(
            ErrorCode.DISCORD_HTTP_ERROR,
            custom_message=f"Ошибка Discord API: {e}",
            details={
                "exception": str(e),
                "status": getattr(e, "status", None),
                "code": getattr(e, "code", None),
            },
        )

    logger.error(f"Unknown error: {e}", exc_info=True)
    return create_error(
        ErrorCode.UNKNOWN_ERROR,
        custom_message=f"Неизвестная ошибка: {e}",
        details={"exception": str(e), "type": type(e).__name__},
    )

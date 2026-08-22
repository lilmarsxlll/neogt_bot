import logging
import sys
from logging.handlers import RotatingFileHandler

from src.config.settings import Environment, settings


def setup_logging() -> logging.Logger:
    """Настраивает систему логирования для бота.

    Конфигурирует console и file handlers в зависимости от окружения.

    Returns:
        Root logger экземпляр.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.get_log_level())

    root_logger.handlers.clear()

    # Убрал противные логи от разных либ из логгера
    logging.getLogger("discord").setLevel(logging.INFO)
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("groq").setLevel(logging.WARNING)

    detailed_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.get_log_level())

    if settings.env == Environment.DEVELOPMENT:
        console_handler.setFormatter(simple_formatter)
    else:
        console_handler.setFormatter(detailed_formatter)

    root_logger.addHandler(console_handler)

    if settings.env == Environment.PRODUCTION:
        settings.log_dir.mkdir(exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=settings.log_dir / "bot.log",
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(settings.get_log_level())
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)

        error_file_handler = RotatingFileHandler(
            filename=settings.log_dir / "errors.log",
            maxBytes=settings.log_max_bytes,
            backupCount=settings.log_backup_count,
            encoding="utf-8",
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(error_file_handler)

    logger = logging.getLogger(__name__)
    logger.info(
        f"Logging initialized in '{settings.env.value}' mode with level '{settings.log_level.value}'"
    )

    if settings.env == Environment.PRODUCTION:
        logger.info(
            f"File logging enabled: {settings.log_dir}/bot.log, {settings.log_dir}/errors.log"
        )

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Получает logger с указанным именем.

    Args:
        name: Имя logger'а (обычно __name__ модуля).

    Returns:
        Logger экземпляр.
    """
    return logging.getLogger(name)

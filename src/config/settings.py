import logging
from enum import Enum
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Окружение приложения."""

    DEVELOPMENT = "development"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Уровень логирования."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """Настройки приложения, загружаемые из .env файла."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    secret_token: str = Field(
        ...,
        description="Discord bot token",
        min_length=1,
    )
    gpt_enabled: bool = Field(default=False, description="Enabled GPT or not")
    gpt_token: str = Field(
        default=None,
        description="Token for GPT integration",
    )
    database_url: str = Field(
        description="Database URL", default="sqlite+aiosqlite:///./bot.db"
    )

    env: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Application environment (development or production)",
    )

    log_level: LogLevel | None = Field(
        default=None,
        description="Logging level (defaults based on environment)",
    )

    log_dir: Path = Field(
        default=Path("logs"),
        description="Directory for log files (production only)",
    )

    log_max_bytes: int = Field(
        default=10 * 1024 * 1024,  # 10 MB
        description="Maximum size of log file before rotation",
        gt=0,
    )

    log_backup_count: int = Field(
        default=5,
        description="Number of backup log files to keep",
        ge=0,
    )

    @field_validator("log_level", mode="before")
    @classmethod
    def set_default_log_level(cls, v: LogLevel | None, info) -> LogLevel:
        """Устанавливает уровень логирования по умолчанию в зависимости от окружения.

        Args:
            v: Переданный уровень логирования.
            info: Контекст валидации Pydantic.

        Returns:
            LogLevel (DEBUG для development, INFO для production).
        """
        if v is not None:
            return v

        env = info.data.get("env", Environment.DEVELOPMENT)

        if env == Environment.DEVELOPMENT:
            return LogLevel.DEBUG
        else:
            return LogLevel.INFO

    def get_log_level(self) -> int:
        """Преобразует LogLevel enum в int значение logging модуля.

        Returns:
            Int значение уровня логирования.
        """
        return getattr(logging, self.log_level.value)


settings = Settings()

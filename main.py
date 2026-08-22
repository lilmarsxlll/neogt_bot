import asyncio
import signal

from src.bot import bot
from src.config.logging_config import get_logger
from src.config.settings import settings
from src.database.engine import engine
from src.discord_modules.cogs.voice_cleanup import setup as setup_voice_cleanup

logger = get_logger(__name__)


async def main():
    """Главная функция для запуска бота."""
    async with bot:
        try:
            logger.info("Starting bot...")
            await setup_voice_cleanup(bot)
            await bot.start(settings.secret_token)

        finally:
            logger.info("Shutting down...")

            await engine.dispose()
            logger.info("Cleanup complete.")


def handle_exit(signum, _):
    """Обработчик для сигнала выхода."""
    logger.info(f"Received signal {signum}, initiating shutdown...")
    raise KeyboardInterrupt


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")

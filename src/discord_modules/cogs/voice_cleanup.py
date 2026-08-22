from discord.ext import commands, tasks

from src.config.const import CLEANUP_INTERVAL_MINUTES
from src.config.logging_config import get_logger
from src.utils.discord_helpers import delete_empty_temp_channels

logger = get_logger(__name__)


class VoiceCleanupCog(commands.Cog):
    """Cog для автоматической очистки пустых приватных голосовых каналов.

    Каждые CLEANUP_INTERVAL_MINUTES (по дефолту 5 минут) сканирует и вызывает
    delete_empty_temp_channels для удаления пустых каналов из приватной категории.

    """

    def __init__(self, bot):
        """Инициализирует VoiceCleanupCog и запускает задачу очистки.

        Args:
            bot: Экземпляр Discord бота
        """
        self.bot = bot
        self.cleanup_task = self.periodic_cleanup
        self.cleanup_task.start()

    def cog_unload(self):
        """Останавливает фоновую задачу очистки при выгрузке Cog."""
        self.cleanup_task.cancel()

    @tasks.loop(minutes=CLEANUP_INTERVAL_MINUTES)
    async def periodic_cleanup(self):
        """Использует delete_empty_temp_channels для удаления пустых рум."""
        if not self.bot.is_ready():
            return

        logger.info(
            f"Cleanup started with interval {CLEANUP_INTERVAL_MINUTES} minutes."
        )
        total_cleaned = 0

        for guild in self.bot.guilds:
            result = await delete_empty_temp_channels(guild)

            if result.is_ok():
                data = result.unwrap()
                total_cleaned += data.deleted_count
                if data.deleted_count > 0:
                    logger.info(
                        f"[{guild.name}]: Deleted {data.deleted_count} channels"
                    )
                if data.error_count > 0:
                    logger.warning(
                        f"[{guild.name}]: {data.error_count} errors during cleanup"
                    )
            else:
                logger.debug(f"[{guild.name}]: {result.error.message}")

        logger.info(f"Total channels cleaned: {total_cleaned} channels.")

    @periodic_cleanup.before_loop
    async def before_periodic_cleanup(self):
        """Ожидает полной готовности бота перед началом периодической очистки."""
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    """Функция для инициации cog внутри discord бота."""
    await bot.add_cog(VoiceCleanupCog(bot))

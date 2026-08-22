import discord

from src.config.logging_config import get_logger
from src.services.helpers import VoiceChannelHelper

logger = get_logger(__name__)


async def cleanup_empty_tmp_channel(before: discord.VoiceState):
    """Обработчик события выхода из голосового канала.

    Удаляет временный приватный канал, если он стал пустым.

    Args:
        before: Состояние голосового канала до изменения.
    """
    if before.channel is None:
        return

    result = await VoiceChannelHelper.cleanup_empty_temporary_channel(before.channel)

    if result.is_err():
        logger.debug(
            f"Could not cleanup channel {before.channel.name}: {result.error.message}"
        )
    else:
        cleanup_data = result.unwrap()
        logger.debug(f"Successfully cleaned up channel {cleanup_data.channel_name}")

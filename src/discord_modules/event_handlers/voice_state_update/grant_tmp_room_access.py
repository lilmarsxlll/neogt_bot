import discord

from src.config.logging_config import get_logger
from src.services.helpers import VoiceChannelHelper

logger = get_logger(__name__)


async def grant_tmp_room_access(member: discord.Member, after: discord.VoiceState):
    """Обработчик события входа в голосовой канал.

    Предоставляет доступ к временному приватному каналу при входе.

    Args:
        member: Участник Discord.
        after: Состояние голосового канала после изменения.
    """
    if after.channel is None:
        return

    result = await VoiceChannelHelper.grant_temporary_room_access(member, after.channel)

    if result.is_err():
        logger.debug(
            f"Could not grant tmp room access to {member.name} for {after.channel.name}: "
            f"{result.error.message}"
        )
    else:
        access_data = result.unwrap()
        if access_data.was_granted:
            logger.debug(
                f"Granted tmp room access to {member.name} for {after.channel.name}"
            )

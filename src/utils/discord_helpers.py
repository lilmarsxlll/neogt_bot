"""Утилиты для взаимодействия с объектами дискорд."""

import discord

from src.common import Error, ErrorCode, Result
from src.common.discord_errors import handle_discord_exception
from src.config.const import PRIVATE_CATEGORY_NAME
from src.config.logging_config import get_logger
from src.services.dto.voice_channels import ChannelsCleanupResult

logger = get_logger(__name__)


def find_category_by_name(
    guild: discord.Guild, category_name: str
) -> discord.CategoryChannel | None:
    """Утилита для нахождения объекта категории внутри определенного дискорд сервера по имени категории.

    Args:
        guild: объект дискорд сервера
        category_name: имя категории

    Returns:
        Объект категории или None, если такая категория не была найдена.
    """
    for category in guild.categories:
        if category.name == category_name:
            return category
    return None


async def delete_empty_temp_channels(
    guild: discord.Guild,
) -> Result[ChannelsCleanupResult, Error]:
    """Удаляет пустые приватные каналы в определенном Сервере.

    Args:
        guild: Объект дискорд сервера

    Returns:
        Result содержит:
            - Ok(ChannelsCleanupResult): DTO результата удаления
            - Fail(Error): Ошибка с кодом ошибки и сообщением для пользователя
    """
    logger.info(f"[{guild.name}] Deleting empty temporary channels...")
    tmp_channel_category = find_category_by_name(guild, PRIVATE_CATEGORY_NAME)

    if tmp_channel_category is None:
        logger.info(f"[{guild.name}] No temporary channels category found.")
        return Result.fail(
            Error(
                code=ErrorCode.CATEGORY_NOT_FOUND,
                message=f"Категория {PRIVATE_CATEGORY_NAME} не найдена",
            )
        )

    deleted_channels = []
    deleted_count = 0
    error_count = 0

    for voice_channel in tmp_channel_category.voice_channels:
        if len(voice_channel.members) == 0:
            logger.debug(
                f"[{guild.name}] Empty tmp channel found: {voice_channel.name}"
            )
            logger.debug(
                f"[{guild.name}] Trying to delete temporary channel: {voice_channel.name}"
            )
            try:
                channel_name = voice_channel.name
                await voice_channel.delete()
                deleted_channels.append(channel_name)
                deleted_count += 1
                logger.debug(
                    f"[{guild.name}] Deleted temporary channel: {channel_name}"
                )
            except Exception as e:
                error = handle_discord_exception(e)
                error_count += 1
                logger.error(
                    f"[{guild.name}] Could not delete temporary channel {voice_channel.name}: {error.message}"
                )

    logger.info(
        f"[{guild.name}] Cleanup completed: {deleted_count} channels deleted, {error_count} errors"
    )
    return Result.ok(
        ChannelsCleanupResult(
            deleted_count=deleted_count,
            deleted_channels=deleted_channels,
            error_count=error_count,
        )
    )

import re

import discord
from discord import app_commands
from discord.ext import commands

from src.config.const import PRIVATE_CATEGORY_NAME
from src.config.logging_config import get_logger
from src.services.helpers import VoiceChannelHelper

member_id_regex = re.compile(r"<@!?(\d+)>")

logger = get_logger(__name__)


@app_commands.command(
    name="make_room", description="Создать приватную комнату для тегнутых гузликов"
)
@app_commands.describe(members="<@user1 @user2 ... @userN>")
async def make_room_command(interaction: discord.Interaction, members: str):
    """Discord slash-команда для создания приватной голосовой комнаты.

    Создаёт приватный канал и перемещает в него упомянутых участников.

    Args:
        interaction: Объект взаимодействия Discord.
        members: Строка с упоминаниями участников (@user1 @user2).
    """
    logger.info(f"Make room call from {interaction.user.name} for {members}")
    member_ids = member_id_regex.findall(members) if members else []

    if not interaction.guild:
        logger.debug("No guild found")
        return

    members_objects = VoiceChannelHelper.resolve_members_from_ids(
        interaction.guild, member_ids
    )

    if len(members_objects) == 0:
        await interaction.response.send_message(
            "Хуево ты как-то натегал...", ephemeral=True
        )
        return
    create_channel_result = await VoiceChannelHelper.create_private_voice_channel(
        interaction.guild, members_objects
    )
    if create_channel_result.is_err():
        await interaction.response.send_message(
            create_channel_result.error.message, ephemeral=True
        )
        return

    channel_data = create_channel_result.unwrap()

    move_members_result = await VoiceChannelHelper.move_members_to_voice_channel(
        interaction.guild, members_objects, channel_data.channel_id
    )
    if move_members_result.is_err():
        await interaction.response.send_message(
            move_members_result.error.message, ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"Успех, мужичок: {channel_data.channel_mention}\n",
        ephemeral=True,
    )
    logger.info(
        f"Successfully created room {channel_data.channel_name} for members: {[i.name for i in members_objects]}.."
    )


@app_commands.command(
    name="make_room_for_us",
    description="Создать приватную комнату для гузликов в текущем голосом канале",
)
async def make_room_for_current_channel(interaction: discord.Interaction):
    """Discord slash-команда для создания приватной комнаты для текущего голосового канала.

    Создаёт приватный канал для всех участников, находящихся в голосовом канале
    с пользователем, вызвавшим команду, и перемещает их туда.

    Args:
        interaction: Объект взаимодействия Discord.
    """
    logger.info(f"Make room for {interaction.user.name} for his current voice channel")
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        logger.info(f"No voice channel found for {interaction.user.name}, return")
        await interaction.response.send_message(
            "Ты додек без канала\n",
            ephemeral=True,
        )
        return
    if (
        interaction.user.voice.channel.category is not None
        and interaction.user.voice.channel.category.name == PRIVATE_CATEGORY_NAME
    ):
        logger.info(f"User {interaction.user.name} already in private room, return")
        await interaction.response.send_message(
            "Ты додек уже в приватке\n",
            ephemeral=True,
        )
        return
    member_ids = [member.id for member in interaction.user.voice.channel.members]
    members = VoiceChannelHelper.resolve_members_from_ids(interaction.guild, member_ids)
    create_channel_result = await VoiceChannelHelper.create_private_voice_channel(
        interaction.guild, members
    )
    if create_channel_result.is_err():
        await interaction.response.send_message(
            create_channel_result.error.message, ephemeral=True
        )
        return

    channel_data = create_channel_result.unwrap()

    move_members_result = await VoiceChannelHelper.move_members_to_voice_channel(
        interaction.guild, members, channel_data.channel_id
    )
    if move_members_result.is_err():
        await interaction.response.send_message(
            move_members_result.error.message, ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"Ибачотко, у вас теперь есть {channel_data.channel_mention}\n",
        ephemeral=True,
    )


def register_make_room_commands(bot: commands.Bot):
    """Регистрирует все slash-команды для создания приватных комнат.

    Args:
        bot: Экземпляр Discord бота.
    """
    logger.debug("Registering make_room commands")

    bot.tree.add_command(make_room_command)
    logger.debug("Registered make_room command")

    bot.tree.add_command(make_room_for_current_channel)
    logger.debug("Registered make_room_for_us command")

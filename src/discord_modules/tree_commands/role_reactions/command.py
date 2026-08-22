import discord
from discord import app_commands
from discord.ext import commands

from src.config.logging_config import get_logger
from src.services import ReactionRoleService

logger = get_logger(__name__)


@app_commands.command(
    name="add_reaction_to_role",
    description="Создает связь реакция-роль",
)
@app_commands.default_permissions(administrator=True)
async def add_reaction_to_role(
    interaction: discord.Interaction, emoji: str, role: discord.Role
):
    """Discord slash-команда для создания связи между реакцией и ролью.

    Доступна только администраторам.

    Args:
        interaction: Объект взаимодействия Discord.
        emoji: Эмоджи для привязки к роли.
        role: Роль Discord для привязки к реакции.
    """
    logger.info(
        f"Add reaction-role call from  {interaction.user.name}. Role-reaction to add {role.name}->{emoji}"
    )
    service: ReactionRoleService = interaction.client.reaction_role_service

    result = await service.add_reaction_to_role(interaction.guild.id, emoji, role)

    if result.is_err():
        await interaction.response.send_message(result.error.message, ephemeral=True)
        return

    reaction_data = result.unwrap()
    logger.info(f"Add reaction-role: {reaction_data.emoji} -> {reaction_data.role_id}")
    await interaction.response.send_message(
        f"Добавлен маппинг {reaction_data.emoji} → {role.mention}", ephemeral=True
    )


@app_commands.command(
    name="remove_reaction_to_role", description="Удаляет связь реакция-роль"
)
@app_commands.default_permissions(administrator=True)
async def remove_reaction_to_role(interaction: discord.Interaction, role: discord.Role):
    """Discord slash-команда для удаления связи между реакцией и ролью.

    Доступна только администраторам.

    Args:
        interaction: Объект взаимодействия Discord.
        role: Роль Discord, связь с которой нужно удалить.
    """
    logger.info(
        f"Remove reaction-role call from  {interaction.user.name}. Remove by role: {role.name}"
    )
    service: ReactionRoleService = interaction.client.reaction_role_service

    result = await service.remove_reaction_to_role(interaction.guild.id, role.id)

    if result.is_err():
        await interaction.response.send_message(result.error.message, ephemeral=True)
        return

    removed_data = result.unwrap()
    logger.info(f"Reaction-role removed (Role {role.name})")
    await interaction.response.send_message(
        f"Удален маппинг {removed_data.emoji} → {role.mention}", ephemeral=True
    )


@app_commands.command(
    name="setup_message",
    description="Создает сгенерированное сообщение с привязкой к ролям",
)
@app_commands.default_permissions(administrator=True)
async def setup_message(interaction: discord.Interaction):
    """Discord slash-команда для создания сообщения с реакциями для выдачи ролей.

    Генерирует или обновляет сообщение со всеми настроенными связями реакция-роль.
    Доступна только администраторам.

    Args:
        interaction: Объект взаимодействия Discord.
    """
    logger.info(f"Setting up reaction-role message. Call from {interaction.user.name}")
    await interaction.response.defer(ephemeral=True)

    service: ReactionRoleService = interaction.client.reaction_role_service
    result = await service.setup_reaction_message(
        interaction.guild, interaction.channel
    )

    if result.is_err():
        await interaction.followup.send(result.error.message, ephemeral=True)
        return

    setup_data = result.unwrap()
    logger.info(
        f"Set up reaction-role message. Reactions added: {setup_data.reactions_added}"
    )
    await interaction.followup.send(
        f"Сообщение с ролями создано: {setup_data.message_url}\n"
        f"Добавлено реакций: {len(setup_data.reactions_added)}\n"
        f"Удалено реакций: {len(setup_data.reactions_removed)}",
        ephemeral=True,
    )


def register_reaction_role_commands(bot: commands.Bot):
    """Регистрирует все slash-команды для управления реакциями на роли.

    Args:
        bot: Экземпляр Discord бота.
    """
    logger.debug("Registering reaction_to_role commands")

    bot.tree.add_command(add_reaction_to_role)
    logger.debug("Registered add_reaction_to_role command")

    bot.tree.add_command(setup_message)
    logger.debug("Registered setup_message command")

    bot.tree.add_command(remove_reaction_to_role)
    logger.debug("Registered remove_reaction_to_role command")

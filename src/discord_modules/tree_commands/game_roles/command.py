import discord
from discord import app_commands
from discord.ext import commands

from src.config.const import GAME_ROLE_PREFIX
from src.config.logging_config import get_logger
from src.services.helpers import DiscordRoleHelper

logger = get_logger(__name__)


@app_commands.command(
    name="create_ping_role",
    description="Создает роль для игры (с префиксом pg_)",
)
@app_commands.describe(role_name="Название роли без каких-либо префиксов")
@app_commands.default_permissions(administrator=True)
async def create_game_role(
    interaction: discord.Interaction,
    role_name: str,
):
    """Discord slash-команда для создания игровой роли.

    Создаёт роль с префиксом pg_ (добавляется автоматически, если отсутствует).
    Доступна только администраторам.

    Args:
        interaction: Объект взаимодействия Discord.
        role_name: Название роли (префикс pg_ добавится автоматически).
    """
    logger.info(f"Create game role call from {interaction.user.name}.")
    if not role_name.startswith("pg_"):
        role_name = f"{GAME_ROLE_PREFIX}{role_name}"
    logger.debug(f"Creating role {role_name}...")

    result = await DiscordRoleHelper.create_game_role(interaction.guild, role_name)

    if result.is_err():
        await interaction.response.send_message(result.error.message, ephemeral=True)
        return

    role_data = result.unwrap()
    logger.info(
        f"Successfully created new game role {role_data.role_name} by {interaction.user.name}"
    )
    await interaction.response.send_message(
        f"Роль {role_data.role_mention} создана успешно", ephemeral=True
    )


@app_commands.command(
    name="delete_ping_role",
    description="Удаляет игровую роль (только с префиксом pg_)",
)
@app_commands.default_permissions(administrator=True)
async def delete_game_role(interaction: discord.Interaction, role: discord.Role):
    """Discord slash-команда для удаления игровой роли.

    Удаляет только роли с префиксом pg_. Доступна только администраторам.

    Args:
        interaction: Объект взаимодействия Discord.
        role: Роль для удаления (должна иметь префикс pg_).
    """
    logger.info(
        f"Delete game role call from {interaction.user.name}. Deleting role {role.name}"
    )
    if not role.name.startswith(GAME_ROLE_PREFIX):
        logger.warning(
            f"Can't delete game role because it doesn't start with {GAME_ROLE_PREFIX}"
        )
        await interaction.response.send_message(
            "Можно только удалять роли @pg_", ephemeral=True
        )
        return
    result = await DiscordRoleHelper.delete_game_role(role)

    if result.is_err():
        await interaction.response.send_message(result.error.message, ephemeral=True)
        return

    role_data = result.unwrap()
    logger.info(f"Successfully deleted game role from {role.name}")
    await interaction.response.send_message(
        f"Роль `{role_data.role_name}` удалена!\n"
        f"Участников было: {role_data.affected_users}",
        ephemeral=True,
    )


def register_game_role_commands(bot: commands.Bot):
    """Регистрирует все slash-команды для управления игровыми ролями.

    Args:
        bot: Экземпляр Discord бота.
    """
    logger.debug("Registering game role commands")

    bot.tree.add_command(create_game_role)
    logger.debug("Registered create_game_role command")

    bot.tree.add_command(delete_game_role)
    logger.debug("Registered delete_game_role command")

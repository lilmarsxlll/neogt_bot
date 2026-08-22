import discord
from discord import app_commands
from discord.ext import commands

from src.config.logging_config import get_logger
from src.discord_modules.tree_commands.help.helpers import (
    build_help_embed,
    get_public_commands,
)
from src.discord_modules.tree_commands.help.view import HelpPaginationView

logger = get_logger(__name__)


@app_commands.command(
    name="help",
    description="Попробуй угадай че это делает",
)
async def help_command(interaction: discord.Interaction):
    """Discord slash-команда для отображения списка публичных команд.

    Собирает все зарегистрированные команды, исключая админские,
    и отображает их в виде интерактивного embed с пагинацией.

    Args:
        interaction: Объект взаимодействия Discord.
    """
    logger.info(f"Help command called by {interaction.user.name}")

    try:
        public_commands = get_public_commands(interaction.client.tree)

        if not public_commands:
            embed = discord.Embed(
                title="Доступные команды",
                description="Публичные команды не найдены.",
                color=discord.Color.pink(),
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        view = HelpPaginationView(public_commands, interaction.user.id)
        embed = build_help_embed(
            view.get_current_page_commands(),
            view.current_page,
            view.total_pages,
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in help command: {e}", exc_info=True)

        error_message = (
            "Произошла ошибка при получении списка команд. Попробуйте позже."
        )

        if not interaction.response.is_done():
            await interaction.response.send_message(error_message, ephemeral=True)
        else:
            await interaction.followup.send(error_message, ephemeral=True)


def register_help_commands(bot: commands.Bot):
    """Регистрирует команду help.

    Args:
        bot: Экземпляр Discord бота.
    """
    logger.debug("Registering help command")
    bot.tree.add_command(help_command)
    logger.debug("Help command registered")

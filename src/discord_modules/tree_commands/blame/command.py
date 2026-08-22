import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import format_dt

from src.config.const import (
    BLAME_GLOBAL_ACTIONS_LIMIT,
    BLAME_MIN_LIMIT,
    BLAME_TARGET_ACTIONS_LIMIT,
)
from src.config.logging_config import get_logger
from src.services.helpers import AuditLogHelper

logger = get_logger(__name__)


@app_commands.command(
    name="blame", description="Отслеживает кто мутил/перемещал пользователя"
)
async def blame(interaction: discord.Interaction):
    """Команда blame - показывает последние действия с каким-то пользователем.

    Собирает перемещения участников по голосовым каналам и муты микрофона
    за последние N минут (5 минут - значение по умолчанию).

    Args:
        interaction: Объект взаимодействия Discord.
    """
    logger.info(f"Blame call by {interaction.user}")

    if not interaction.guild:
        await interaction.response.send_message("No guild", ephemeral=True)
        return

    blame_result = await AuditLogHelper.get_recent_actions(
        interaction.guild,
        interaction.user,
        time_window_minutes=BLAME_MIN_LIMIT,
        target_actions_limit=BLAME_TARGET_ACTIONS_LIMIT,
        global_actions_limit=BLAME_GLOBAL_ACTIONS_LIMIT,
    )

    if blame_result.is_err():
        await interaction.response.send_message(
            blame_result.error.message, ephemeral=True
        )
        return

    blame_data = blame_result.unwrap()
    if not blame_data.actions:
        await interaction.response.send_message(
            f"За последние {BLAME_MIN_LIMIT} мин никаких гузликов не трогали",
            ephemeral=True,
        )
        return

    targeted_actions = blame_data.targeted_actions
    global_actions = blame_data.global_actions

    lines: list[str] = []

    if targeted_actions:
        lines.append("**ДЕЙСТВИЯ НАД ТОБОЙ**")
        for i, action in enumerate(targeted_actions, 1):
            lines.append(
                f"{i}. {action.user_message} — {format_dt(action.created_at, 'R')}"
            )

    if global_actions:
        if targeted_actions:
            lines.append("")  # пустая строка между секциями
        lines.append("**ОБЩИЕ ДЕЙСТВИЯ**")
        for i, action in enumerate(global_actions, 1):
            lines.append(
                f"{i}. {action.user_message} — {format_dt(action.created_at, 'R')}"
            )

    embed = discord.Embed(
        description="\n".join(lines),
        color=discord.Color.pink(),
        timestamp=discord.utils.utcnow(),
    )

    await interaction.response.send_message(embed=embed, ephemeral=False)


def register_blame_commands(bot: commands.Bot):
    """Регистрирует команду blame.

    Args:
        bot: Экземпляр Discord бота.
    """
    logger.debug("Registering blame command")
    bot.tree.add_command(blame)
    logger.debug("Blame command registered")

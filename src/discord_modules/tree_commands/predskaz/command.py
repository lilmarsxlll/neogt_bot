import discord
from discord import app_commands
from discord.ext import commands

from src.config.logging_config import get_logger
from src.services.helpers.message import DiscordMessageHelper
from src.services.predskaz_service import PredskazGenerator

logger = get_logger(__name__)

generator = PredskazGenerator()


@app_commands.command(name="predskaz", description="Узнать свое предсказание")  # noqa
@app_commands.checks.cooldown(rate=1, per=5.0)
async def predskaz_command(interaction: discord.Interaction):
    """Команда predskaz - выдает случайную фразу для вызвавшего.

    Args:
        interaction: Объект взаимодействия Discord.
    """
    logger.info(f"Make predskaz for {interaction.user.name}")

    if not interaction.guild:
        logger.debug("No guild found")
        return

    await interaction.response.defer()

    template = generator.generate_template()

    predskaz = generator.compute_template(
        template, interaction.guild.members, interaction.user  # noqa
    )

    embed = discord.Embed(
        title=f"Предсказание для {interaction.user.display_name}",
        description=predskaz,
        color=DiscordMessageHelper.get_random_embed_color(),
    )

    await interaction.followup.send(embed=embed)


@predskaz_command.error
async def predskaz_command_error(
    interaction: discord.Interaction, error: app_commands.AppCommandError
):
    """Функция, ответственная за отлов ошибки CommandOnCooldown."""
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"Подожди {int(error.retry_after)} сек перед следующим предсказанием, маленький спамер.",
            ephemeral=True,
        )


def register_predskaz_command(bot: commands.Bot):
    """Регистрирует команда predskaz.

    Args:
        bot: Экземпляр Discord бота.
    """
    logger.debug("Registering predskaz command")
    bot.tree.add_command(predskaz_command)
    logger.debug("Registered predskaz command")

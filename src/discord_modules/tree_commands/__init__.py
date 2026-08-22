from discord.ext import commands

from src.discord_modules.tree_commands.blame import register_blame_commands
from src.discord_modules.tree_commands.game_roles import register_game_role_commands
from src.discord_modules.tree_commands.help import register_help_commands
from src.discord_modules.tree_commands.make_room import register_make_room_commands
from src.discord_modules.tree_commands.predskaz import register_predskaz_command
from src.discord_modules.tree_commands.role_reactions import (
    register_reaction_role_commands,
)


def register_all_commands(bot: commands.Bot):
    """Регистрирует все slash-команды Discord бота.

    Args:
        bot: Экземпляр Discord бота.
    """
    register_make_room_commands(bot)
    register_reaction_role_commands(bot)
    register_game_role_commands(bot)
    register_blame_commands(bot)
    register_predskaz_command(bot)
    register_help_commands(bot)

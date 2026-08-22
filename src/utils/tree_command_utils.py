"""Утилиты для работы с tree commands."""

import discord


def parse_tree_commands(
    tree_commands: list[discord.app_commands.AppCommand],
) -> list[str]:
    """Извлекает имена из списка AppCommands.

    Args:
        tree_commands: список AppCommands

    Returns:
        Список, состоящий только из "имен" этих команд

    Examples:
        >>> from discord.app_commands import AppCommand
        >>> tree_commands_list = [AppCommand(name="app_cmd_name"), AppCommand(name="ping")]
        >>> parse_tree_commands(tree_commands_list)
        ["app_cmd_name", "ping"]
    """
    return [i.name for i in tree_commands]

import discord
from discord import app_commands


def format_param(param: app_commands.Parameter) -> str:
    """Форматирует параметр для отображения в help.

    Использует description параметра если задан через @app_commands.describe(),
    иначе использует имя параметра.

    Args:
        param: Объект параметра команды.

    Returns:
        Отформатированное представление параметра.
    """
    if param.description:
        return param.description

    return f"<{param.name}>"


def get_public_commands(tree: app_commands.CommandTree) -> list[app_commands.Command]:
    """Получает список публичных (не-админских) команд.

    Args:
        tree: Дерево команд Discord бота.

    Returns:
        Список публичных команд.
    """
    public_commands = []

    for cmd in tree.walk_commands():
        if not hasattr(cmd, "parameters"):
            continue

        if hasattr(cmd, "default_permissions"):
            perms = cmd.default_permissions
            if perms and perms.administrator:
                continue

        public_commands.append(cmd)

    return public_commands


def build_help_embed(
    commands_list: list[app_commands.Command],
    page: int,
    total_pages: int,
) -> discord.Embed:
    """Создает embed для страницы help.

    Args:
        commands_list: Список команд для текущей страницы.
        page: Номер текущей страницы (начиная с 0).
        total_pages: Общее количество страниц.

    Returns:
        Embed с командами для текущей страницы.
    """
    embed = discord.Embed(
        title="Доступные команды",
        description="Вникай епта",
        color=discord.Color.pink(),
    )

    for cmd in commands_list:
        params_list = []
        if hasattr(cmd, "parameters"):
            for param in cmd.parameters:
                formatted = format_param(param)
                if formatted:
                    params_list.append(formatted)

        params_str = " ".join(params_list) if params_list else ""

        cmd_display = f"/{cmd.name}"
        if params_str:
            cmd_display += f" {params_str}"

        embed.add_field(
            name=cmd_display,
            value=cmd.description or "Без описания",
            inline=False,
        )

    embed.set_footer(text=f"Страница {page + 1} из {total_pages}")

    return embed

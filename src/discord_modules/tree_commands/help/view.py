import discord
from discord import app_commands

from src.config.const import MAX_COMMANDS_PER_PAGE
from src.discord_modules.tree_commands.help.helpers import (
    build_help_embed,
)


class HelpPaginationView(discord.ui.View):
    """View с кнопками пагинации для команды help."""

    def __init__(
        self,
        commands_list: list[app_commands.Command],
        author_id: int,
        timeout: float = 120.0,
    ):
        """Инициализирует view пагинации.

        Args:
            commands_list: Полный список команд.
            author_id: ID пользователя, вызвавшего команду.
            timeout: Таймаут в секундах до отключения кнопок.
        """
        super().__init__(timeout=timeout)
        self.commands_list = commands_list
        self.author_id = author_id
        self.current_page = 0
        self.total_pages = (
            len(commands_list) + MAX_COMMANDS_PER_PAGE - 1
        ) // MAX_COMMANDS_PER_PAGE

        self._update_buttons()

    def get_current_page_commands(self) -> list[app_commands.Command]:
        """Возвращает команды для текущей страницы."""
        start = self.current_page * MAX_COMMANDS_PER_PAGE
        end = start + MAX_COMMANDS_PER_PAGE
        return self.commands_list[start:end]

    def _update_buttons(self):
        """Обновляет состояние кнопок в зависимости от текущей страницы."""
        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= self.total_pages - 1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Проверяет, что взаимодействует автор команды.

        Args:
            interaction: Объект взаимодействия Discord.

        Returns:
            True если взаимодействует автор, иначе False.
        """
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Эти кнопки не для тебя, вызови /help сам",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="<", style=discord.ButtonStyle.secondary)
    async def prev_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Обработчик кнопки 'назад'.

        Args:
            interaction: Объект взаимодействия Discord.
            button: Объект кнопки.
        """
        self.current_page -= 1
        self._update_buttons()

        embed = build_help_embed(
            self.get_current_page_commands(),
            self.current_page,
            self.total_pages,
        )
        await interaction.response.edit_message(embed=embed, view=self)

    @discord.ui.button(label=">", style=discord.ButtonStyle.secondary)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """Обработчик кнопки 'вперед'.

        Args:
            interaction: Объект взаимодействия Discord.
            button: Объект кнопки.
        """
        self.current_page += 1
        self._update_buttons()

        embed = build_help_embed(
            self.get_current_page_commands(),
            self.current_page,
            self.total_pages,
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self):
        """Отключает кнопки по истечении таймаута."""
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

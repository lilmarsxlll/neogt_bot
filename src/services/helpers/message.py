import random

import discord


class DiscordMessageHelper:
    """Класс с методами для работы с ембедами/сообщениями."""

    @staticmethod
    def get_random_embed_color() -> discord.Color:
        """Возвращает случайный цвет для дискорд ембед."""
        return discord.Color(random.randint(0x444444, 0xFFFFFF))

import random
import re

from discord import Member

from src.config.const import GPT_MODELS, GPT_PROMPT, PREDSKAZ_SECRET, PREDSKAZ_STATIC
from src.config.logging_config import get_logger
from src.config.settings import settings
from src.services.helpers.gpt_generator import GroqClientHelper

logger = get_logger(__name__)


class PredskazGenerator:
    """Генератор предсказаний с секретной фразой."""

    def __init__(self) -> None:
        self.templates = PREDSKAZ_STATIC
        self.secret_phrase = PREDSKAZ_SECRET
        self._groq_helper = GroqClientHelper()

    def generate_template(self) -> str:
        """Выбирает случайный шаблон для отправки на основе весов."""
        methods = [
            self.__generate_secret,
            self.__generate_from_static,
            self.__generate_gpt_template,
        ]
        weights = [0.1, 30.0, 69.9]

        chosen_method = random.choices(methods, weights=weights, k=1)[0]
        return chosen_method()

    def __generate_from_static(self) -> str:
        return random.choice(self.templates)

    def __generate_secret(self) -> str:
        return self.secret_phrase

    def __generate_gpt_template(self) -> str:
        if not settings.gpt_enabled:
            logger.warning("GPT generation disabled, falling back to static")
            return self.__generate_from_static()

        model = random.choice(GPT_MODELS)
        logger.debug(f"Using GPT model: {model.display_name}")
        gpt_prompt_copy = GPT_PROMPT
        for _ in range(10):
            rnd_predskaz = random.choice(PREDSKAZ_STATIC)
            gpt_prompt_copy = gpt_prompt_copy + rnd_predskaz + "." + "\n"

        result = self._groq_helper.generate(gpt_prompt_copy, model.model_id)
        if result.is_err():
            logger.error(
                f"GPT generation failed ({model.display_name}): {result.error}"
            )
            return self.__generate_from_static()

        return f"[сгенерировано]: {result.unwrap()}"

    @staticmethod
    def _get_random_member(members: list[Member], author: Member) -> str:
        """Выбирает случайного участника сервера (исключая ботов и автора команды).

        Args:
            members: Список всех участников.
            author: Отправитель команды.

        Returns:
            str: Упоминание юзера или автора при отсутствии юзера.
        """
        candidates = [mem for mem in members if not mem.bot and mem != author]
        if candidates:
            return random.choice(candidates).mention
        logger.debug("No candidates for member selection")
        return author.mention

    def compute_template(
        self, template: str, guild_members: list[Member], author: Member
    ) -> str:
        """Обрабатывает шаблон, заменяя {RANDOM_INT} и {RANDOM_DISC_MEMBER} на случайные значения.

        Args:
            template: Шаблон
            guild_members: Список участников
            author: Отправитель команды команды

        Returns:
            str: Готовое предсказание с подставленными значениями
        """
        replacers = {
            "RANDOM_INT": lambda: str(random.randint(1, 100)),
            "RANDOM_DISC_MEMBER": lambda: self._get_random_member(
                guild_members, author
            ),
        }

        def replace(match: re.Match) -> str:
            key = match.group(1)
            if key in replacers:
                return replacers[key]()
            return match.group(0)

        result = re.sub(r"\{(\w+)\}", replace, template)

        logger.debug("Computed predskaz")
        return result

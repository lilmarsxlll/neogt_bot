from groq import Groq

from src.common import Error, ErrorCode, Result
from src.config.logging_config import get_logger
from src.config.settings import settings

logger = get_logger(__name__)


class GroqClientHelper:
    """Helper для работы с Groq API."""

    _instance: "GroqClientHelper | None" = None
    _client: Groq | None = None

    def __new__(cls) -> "GroqClientHelper":
        """Реализация singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def client(self) -> Groq:
        """Ленивая инициализация Groq клиента."""
        if self._client is None:
            self._client = Groq(api_key=settings.gpt_token)
            logger.debug("Groq client initialized")
        return self._client

    def generate(self, prompt: str, model_id: str) -> Result[str, Error]:
        """Генерирует ответ через Groq API.

        Args:
            prompt: Текст промпта.
            model_id: ID модели для генерации.

        Returns:
            Result содержит:
                - Ok(str): Сгенерированный текст.
                - Fail(Error): Ошибка при генерации.
        """
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],  # NOQA
                model=model_id,
            )
            content = chat_completion.choices[0].message.content
            return Result.ok(content)
        except Exception as e:
            logger.error(f"Groq generation failed: {e}")
            return Result.fail(
                Error(
                    code=ErrorCode.GPT_GENERATION_FAILED,
                    message="Ошибка генерации GPT",
                    details={"error": str(e)},
                )
            )

"""Утилиты для генерации случайного имени канала в дискорде."""

import random

from src.config.const import (
    ADJECTIVES,
    MAX_COUNT_FOR_ROOM,
    MIN_COUNT_FOR_ROOM,
    NOUNS,
    TMP_CHANNEL_PREFIX,
)
from src.config.logging_config import get_logger

logger = get_logger(__name__)


def generate_name():
    """Генерирует имя для канала в дискорде с низким шансом пересечения результата.

    Returns:
          Имя для дискорд канала

    Examples:
        >>> generate_name()
        "tmpr_MegaBonk1337"
    """
    adj = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    unique_num = random.randint(MIN_COUNT_FOR_ROOM, MAX_COUNT_FOR_ROOM)

    name = f"{TMP_CHANNEL_PREFIX}_{adj}{noun}{unique_num}"
    logger.debug(f"Generated name for private room: {name}")

    return name

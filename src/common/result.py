from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E")


@dataclass(frozen=True)
class Result(Generic[T, E]):
    """Result type для type-safe обработки ошибок.

    Generic тип Result[T, E] может содержать либо успешное значение типа T,
    либо ошибку типа E, но не оба одновременно.

    Attributes:
        _value: Успешное значение (если Result содержит Ok).
        _error: Ошибка (если Result содержит Err).
    """

    _value: T | None = None
    _error: E | None = None

    def __post_init__(self):
        if (self._value is None) == (self._error is None):
            raise ValueError(
                "Result must have either value or error, not both or neither"
            )

    @staticmethod
    def ok(value: T) -> "Result[T, E]":
        """Создаёт успешный Result с значением.

        Args:
            value: Значение успешного результата.

        Returns:
            Result[T, E] содержащий значение.
        """
        return Result(_value=value, _error=None)

    @staticmethod
    def fail(error: E) -> "Result[T, E]":
        """Создаёт Result с ошибкой.

        Args:
            error: Ошибка.

        Returns:
            Result[T, E] содержащий ошибку.
        """
        return Result(_value=None, _error=error)

    def is_ok(self) -> bool:
        """Проверяет, является ли Result успешным.

        Returns:
            True если Result содержит значение, False если ошибку.
        """
        return self._error is None

    def is_err(self) -> bool:
        """Проверяет, является ли Result ошибкой.

        Returns:
            True если Result содержит ошибку, False если значение.
        """
        return self._error is not None

    def unwrap(self) -> T:
        """Извлекает значение из Result.

        Returns:
            Значение из Ok Result.

        Raises:
            ValueError: Если Result содержит ошибку.
        """
        if self.is_err():
            raise ValueError(f"Called unwrap on error result: {self._error}")
        return self._value

    @property
    def value(self) -> T | None:
        return self._value

    @property
    def error(self) -> E | None:
        return self._error

    def __repr__(self) -> str:
        if self.is_ok():
            return f"Ok({self._value!r})"
        return f"Err({self._error!r})"

    def __str__(self) -> str:
        return self.__repr__()

# neogt_bot

Бот, созданный для личного пользования некоторым сервером DISCORD для NEOGT людей.

## Требования

- Python 3.14+
- Poetry для управления зависимостями

## Установка

1. Накатить poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Установить зависимости (включая dev-зависимости для линтеров):
```bash
poetry install --with dev
```

3. Создайте файл `.env` из примера:
```bash
cp .env_example .env
```

4. Заполните `.env` файл:
   - `secret_token` - токен нашего Discord бота
   - `guild_id` - ID нашего Discord сервера

## Запуск бота

```bash
poetry run python3 main.py
```

## Разработка

### Линтеры и форматирование

Проект использует Ruff (линтер + форматтер).

Проверка кода:
```bash
# Форматирование кода
poetry run black .

# Проверка с помощью ruff
poetry run ruff check .

# Автоматическое исправление проблем
poetry run ruff check --fix .
```
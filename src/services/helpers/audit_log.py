from datetime import UTC, datetime, timedelta

import discord

from src.common import Error, Result
from src.common.discord_errors import handle_discord_exception
from src.config.logging_config import get_logger
from src.services.dto.blame import (
    Action,
    BlameResult,
    DeafenAction,
    MoveAction,
    MuteAction,
)

logger = get_logger(__name__)


class AuditLogHelper:
    """Хелпер для работы с AuditLog'ом дискорда."""

    @staticmethod
    async def get_recent_actions(
        guild: discord.Guild,
        target_user: discord.User | discord.Member,
        *,
        time_window_minutes: int,
        target_actions_limit: int,
        global_actions_limit: int,
    ) -> Result[BlameResult, Error]:
        """Собирает недавние действия из журнала аудита для команды blame.

        Args:
            guild: Discord-сервер
            target_user: Пользователь, для которого ищем целевые действия
            time_window_minutes: Временное окно в минутах для поиска
            target_actions_limit: Лимит целевых действий (мут/оглушение)
            global_actions_limit: Лимит общих действий (перемещения)

        Returns:
            Result содержит:
                - Ok(BlameResult): Список собранных действий и их количество
                - Fail(Error): Ошибка при обработке Discord исключений
        """
        try:
            audit_time = datetime.now(UTC) - timedelta(minutes=time_window_minutes)
            actions = await AuditLogHelper.__collect_auditlogs(
                guild,
                target_user,
                audit_time,
                target_actions_limit,
                global_actions_limit,
            )

            logger.info(
                f"Found {len(actions)} audit logs in last {time_window_minutes} minutes"
            )

            return Result.ok(BlameResult(actions=actions))

        except Exception as e:
            error = handle_discord_exception(e)
            logger.error(f"Audit log error: {error}")
            return Result.fail(error)

    @staticmethod
    async def __collect_auditlogs(
        guild: discord.Guild,
        target_user: discord.User | discord.Member,
        audit_time: datetime,
        target_action_limit: int,
        global_actions_limit: int,
    ) -> list[Action]:
        """Собирает действия с голосом из журнала аудита (перемещения, муты, оглушения).

        Args:
            guild: Discord-сервер
            target_user: Пользователь, для которого ищем целевые действия
            audit_time: Самое раннее время для рассмотрения
            target_action_limit: Лимит целевых действий (мут/оглушение)
            global_actions_limit: Лимит общих действий (перемещения)

        Returns:
            Список объектов BlameAction
        """
        logger.debug(f"Collecting audit logs for {guild.name}")
        targeted_actions: list[MuteAction | DeafenAction] = []
        global_actions: list[MoveAction] = []

        logger.debug("Gathering blame actions..")
        async for entry in guild.audit_logs(limit=100):
            if entry.created_at < audit_time:
                break

            # Оба лимита достигнуты
            if (
                len(targeted_actions) >= target_action_limit
                and len(global_actions) >= global_actions_limit
            ):
                break

            if entry.user is None or entry.user.bot:
                continue

            # перемещение
            if entry.action == discord.AuditLogAction.member_move:
                if len(global_actions) >= global_actions_limit:
                    continue
                if entry.extra is None or entry.extra.channel is None:
                    continue
                global_actions.append(
                    MoveAction(
                        user_mention=entry.user.mention,
                        channel_mention=entry.extra.channel.mention,
                        move_count=entry.extra.count,
                        created_at=entry.created_at,
                    )
                )
                logger.debug(
                    f"Move action gathered. Global actions: {len(global_actions)}"
                )

            # мут или офф звука
            elif entry.action == discord.AuditLogAction.member_update:
                if len(targeted_actions) >= target_action_limit:
                    continue
                if entry.target is None or entry.target.id != target_user.id:
                    continue

                is_mute = getattr(entry.changes.after, "mute", None)
                is_deaf = getattr(entry.changes.after, "deaf", None)

                if is_mute:
                    targeted_actions.append(
                        MuteAction(
                            user_mention=entry.user.mention,
                            target_mention=entry.target.mention,
                            created_at=entry.created_at,
                        )
                    )
                    logger.debug(
                        f"Mute action gathered. Targeted actions: {len(targeted_actions)}"
                    )
                elif is_deaf:
                    targeted_actions.append(
                        DeafenAction(
                            user_mention=entry.user.mention,
                            target_mention=entry.target.mention,
                            created_at=entry.created_at,
                        )
                    )
                    logger.debug(
                        f"Deafen action gathered. Targeted actions: {len(targeted_actions)}"
                    )

        actions: list[Action] = [*targeted_actions, *global_actions]
        logger.debug(f"Total actions {len(actions)}")

        return actions

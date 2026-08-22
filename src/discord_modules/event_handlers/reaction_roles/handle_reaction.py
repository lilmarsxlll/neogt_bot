import discord

from src.config.const import RoleAction
from src.config.logging_config import get_logger
from src.services.helpers import DiscordRoleHelper
from src.services.reaction_role_service import ReactionRoleService

logger = get_logger(__name__)


async def handle_reaction(
    service: ReactionRoleService,
    payload: discord.RawReactionActionEvent,
    guild: discord.Guild,
    action: RoleAction,
):
    """Обработчик событий добавления/удаления реакции.

    Выдаёт или забирает роль у участника в зависимости от реакции.

    Args:
        service: Сервис для работы с реакциями на роли.
        payload: Данные события реакции.
        guild: Discord-сервер.
        action: Действие (ADD или REMOVE).
    """
    discord_role = await service.resolve_role_from_reaction(payload, guild)

    if not discord_role:
        logger.debug(f"Role from emoji {payload.emoji} not found in guild {guild.id}")
        return

    member = guild.get_member(payload.user_id)
    if not member:
        logger.debug(f"Member {payload.user_id} not found in guild {guild.id}")
        return

    result = await DiscordRoleHelper.apply_role_to_member(member, discord_role, action)

    if result.is_err():
        logger.error(
            f"Failed to {action} role {discord_role.name} for {member.name}: "
            f"{result.error.message}"
        )
    else:
        role_data = result.unwrap()
        logger.info(
            f"Successfully applied role {role_data.role_name} to {member.name} "
            f"(action: {action})"
        )

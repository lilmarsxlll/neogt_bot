import discord

from src.config.const import BasicRolesForOlds, RoleAction
from src.config.logging_config import get_logger
from src.services.helpers import DiscordRoleHelper

logger = get_logger(__name__)


async def assign_user_role_on_join(member: discord.Member):
    """Обработчик события присоединения нового участника к серверу.

    Автоматически назначает базовые роли новым участникам.

    Args:
        member: Новый участник Discord.
    """
    # TODO: переделать под БД и сервис в соотв. задаче
    logger.info(f"Assigning basic user roles to {member.name}...")
    for role in BasicRolesForOlds:
        dis_role = discord.utils.get(member.guild.roles, name=role.value)
        if not dis_role:
            logger.warning(f"Role {role.value} not found in guild {member.guild.id}")
            continue

        result = await DiscordRoleHelper.apply_role_to_member(
            member, dis_role, RoleAction.ADD
        )

        if result.is_err():
            logger.error(
                f"Failed to assign role {role.value} to {member.name}: "
                f"{result.error.message}"
            )
        else:
            role_data = result.unwrap()
            logger.debug(f"Assigned role {role_data.role_name} to {member.name}")

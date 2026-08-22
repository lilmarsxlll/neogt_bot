import discord

from src.common import Error, ErrorCode, Result
from src.common.discord_errors import handle_discord_exception
from src.config.const import RoleAction
from src.config.logging_config import get_logger
from src.services.dto.game_roles import GameRoleResult, RoleApplyResult

logger = get_logger(__name__)


class DiscordRoleHelper:
    """Хелпер для работы с ролями Discord.

    Предоставляет статические методы для добавления/удаления ролей
    и управления игровыми ролями.
    """

    @staticmethod
    async def apply_role_to_member(
        member: discord.Member, role: discord.Role, action: RoleAction
    ) -> Result[RoleApplyResult, Error]:
        """Добавляет или удаляет роль участнику.

        Args:
            member: Участник Discord.
            role: Роль для применения.
            action: Действие (ADD или REMOVE).

        Returns:
            Result содержит:
                - Ok(RoleApplyResult): DTO с информацией о применении роли
                - Fail(Error): Ошибка Discord API
        """
        if action == RoleAction.ADD and role in member.roles:
            logger.debug(f"User {member.name} already has role {role.name}")
            return Result.ok(
                RoleApplyResult(
                    member_id=member.id,
                    member_name=member.name,
                    role_id=role.id,
                    role_name=role.name,
                    action=RoleAction.ADD,
                )
            )

        if action == RoleAction.REMOVE and role not in member.roles:
            logger.debug(f"User {member.name} already without role {role.name}")
            return Result.ok(
                RoleApplyResult(
                    member_id=member.id,
                    member_name=member.name,
                    role_id=role.id,
                    role_name=role.name,
                    action=RoleAction.REMOVE,
                )
            )

        try:
            if action == RoleAction.ADD:
                await member.add_roles(role)
            else:
                await member.remove_roles(role)

            return Result.ok(
                RoleApplyResult(
                    member_id=member.id,
                    member_name=member.name,
                    role_id=role.id,
                    role_name=role.name,
                    action=action,
                )
            )

        except Exception as e:
            error = handle_discord_exception(e)
            logger.error(
                f"Failed to {action} role {role.name} for {member.name}: {error}"
            )
            return Result.fail(error)

    @staticmethod
    async def create_game_role(
        guild: discord.Guild, full_name: str
    ) -> Result[GameRoleResult, Error]:
        """Создаёт новую игровую роль на сервере.

        Args:
            guild: Discord-сервер.
            full_name: Полное название роли.

        Returns:
            Result содержит:
                - Ok(GameRoleResult): DTO созданной роли
                - Fail(Error): Ошибка с кодом ROLE_ALREADY_EXISTS или Discord API ошибка
        """
        existing_role = discord.utils.get(guild.roles, name=full_name)
        if existing_role:
            logger.warning(f"Role {full_name} already exists")
            return Result.fail(
                Error(
                    code=ErrorCode.ROLE_ALREADY_EXISTS,
                    message=f"Роль {existing_role.mention} уже существует!",
                    details={"role_id": existing_role.id, "role_name": full_name},
                )
            )

        try:
            role = await guild.create_role(
                name=full_name,
                mentionable=True,
                hoist=False,
                reason="Game role created by NEOGT_bot",
            )
            logger.debug(f"Created game role: {role.name} (ID: {role.id})")

            return Result.ok(
                GameRoleResult(
                    role_name=role.name,
                    role_mention=role.mention,
                    role_id=role.id,
                    affected_users=0,
                )
            )

        except Exception as e:
            error = handle_discord_exception(e)
            logger.error(f"Failed to create game role {full_name}: {error}")
            return Result.fail(error)

    @staticmethod
    async def delete_game_role(role: discord.Role) -> Result[GameRoleResult, Error]:
        """Удаляет игровую роль с сервера.

        Args:
            role: Роль Discord для удаления.

        Returns:
            Result содержит:
                - Ok(GameRoleResult): DTO удалённой роли с количеством затронутых участников
                - Fail(Error): Ошибка Discord API
        """
        member_count = len(role.members)
        role_name = role.name
        role_id = role.id

        try:
            await role.delete(reason="Deleted by NEOGT_bot")
            return Result.ok(
                GameRoleResult(
                    role_name=role_name,
                    role_mention=f"@{role_name}",
                    role_id=role_id,
                    affected_users=member_count,
                )
            )

        except Exception as e:
            error = handle_discord_exception(e)
            logger.error(f"Failed to delete game role {role_name}: {error}")
            return Result.fail(error)

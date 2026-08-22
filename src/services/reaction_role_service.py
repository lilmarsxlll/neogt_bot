from collections.abc import Callable

import discord
from pydantic import ValidationError

from src.common import Error, ErrorCode, Result
from src.common.discord_errors import handle_discord_exception
from src.config.logging_config import get_logger
from src.database.models.reaction_role import ReactionRole
from src.database.models.role_message import RoleMessage
from src.database.unit_of_work import UnitOfWork
from src.services.dto import (
    ReactionRoleDTO,
    ReactionRoleListDTO,
    RoleMessageDTO,
    SetupMessageResult,
)

logger = get_logger(__name__)


class ReactionRoleService:
    """Сервис для управления системой ролей через постановку реакций.

    Предоставляет функциональность для:
    - Создания/удаления связей между эмоджи и ролями
    - Настройки сообщений с реакциями в Discord
    - Определения ролей по реакциям пользователей
    """

    def __init__(
        self,
        uow_factory: Callable[[], UnitOfWork],
        bot: discord.Client | None = None,
    ):
        self._uow_factory = uow_factory
        self._bot = bot

    async def add_reaction_to_role(
        self, guild_id: int, emoji: str, role: discord.Role
    ) -> Result[ReactionRoleDTO, Error]:
        """Добавляет или обновляет связь между реакцией и ролью.

        При наличии существующей связи с тем же эмоджи или той же ролью,
        старая связь удаляется и создаётся новая.

        Args:
            guild_id: ID Discord-сервера.
            emoji: Строка с эмоджи (Unicode или Discord custom <:name:id>).
            role: Discord роль для привязки к реакции.

        Returns:
            Result содержит:
                - Ok(ReactionRoleDTO): DTO созданной связи
                - Fail(Error): Ошибка с кодом INVALID_EMOJI при невалидном формате
        """
        logger.debug(
            f"Adding reaction to role {guild_id} with emoji {emoji} and role {role.name}"
        )

        async with self._uow_factory() as uow:
            logger.debug("Trying to find existing react to role...")
            existing_by_emoji = await uow.reaction_roles.get_by_guild_and_emoji(
                guild_id, emoji
            )
            existing_by_role_id = await uow.reaction_roles.get_role_by_role_id(
                guild_id, role.id
            )
            existing = existing_by_emoji or existing_by_role_id

            if existing:
                logger.debug(
                    f"Found existing react to role {existing.id} (emoji {emoji} → role {existing.role_id}), removing old"
                )
                await uow.reaction_roles.remove_reaction_role(
                    guild_id, existing.role_id
                )
                await uow.flush()

            reaction_role = await uow.reaction_roles.add_reaction_role(
                guild_id, role.id, emoji
            )
            try:
                mapped_dto = self._map_to_dto(reaction_role)
                return Result.ok(mapped_dto)
            except ValidationError as e:
                await uow.rollback()
                return Result.fail(
                    Error(
                        code=ErrorCode.INVALID_EMOJI,
                        message="Некорректный формат эмоджи",
                        details={"validation_error": e},
                    )
                )

    async def remove_reaction_to_role(
        self, guild_id: int, role_id: int
    ) -> Result[ReactionRoleDTO, Error]:
        """Удаляет связь между реакцией и ролью.

        Args:
            guild_id: ID Discord-сервера.
            role_id: ID роли для удаления связи.

        Returns:
            Result содержит:
                - Ok(ReactionRoleDTO): DTO удалённой связи
                - Fail(Error): Ошибка с кодом REACTION_ROLE_NOT_FOUND, если связь не найдена
        """
        async with self._uow_factory() as uow:
            existing = await uow.reaction_roles.get_role_by_role_id(guild_id, role_id)

            if not existing:
                logger.warning(f"No mapping found for role {role_id}")
                return Result.fail(
                    Error(
                        code=ErrorCode.REACTION_ROLE_NOT_FOUND,
                        message="Связь реакции с ролью не найдена",
                        details={"guild_id": guild_id, "role_id": role_id},
                    )
                )

            removed_dto = self._map_to_dto(existing)
            await uow.reaction_roles.remove_reaction_role(guild_id, role_id)

            return Result.ok(removed_dto)

    async def get_all_reaction_roles(self, guild_id: int) -> ReactionRoleListDTO:
        """Получает все связи реакция-роль для указанного сервера.

        Args:
            guild_id: ID Discord-сервера.

        Returns:
            ReactionRoleListDTO со всеми связями и общим количеством.
        """
        async with self._uow_factory() as uow:
            reactions = await uow.reaction_roles.get_all_by_guild(guild_id)

            return ReactionRoleListDTO(
                guild_id=guild_id,
                mappings=[self._map_to_dto(r) for r in reactions],
                total_count=len(reactions),
            )

    async def setup_reaction_message(
        self,
        guild: discord.Guild,
        channel: discord.TextChannel,
    ) -> Result[SetupMessageResult, Error]:
        """Создает/редактирует отслеживаемое сообщение для реагирования на поставленные реакции.

        Args:
            guild: объект дискорд сервера
            channel: объект текстового канала, где была вызвана команда

        Returns:
            Result содержит:
                - Ok(SetupMessageResult): DTO об успешном выполнении метода
                - Fail(Error): Ошибка с кодом ошибки и сообщением для пользователя
        """
        async with self._uow_factory() as uow:
            existing_msg = await uow.role_messages.get_by_guild_id(guild.id)
            old_discord_msg = None

            if existing_msg:
                old_discord_msg = await self._fetch_existing_message(
                    guild, existing_msg, uow
                )

            all_reactions = await uow.reaction_roles.get_all_by_guild(guild.id)

            if not all_reactions:
                logger.warning(f"No reaction roles configured for guild {guild.id}")
                if old_discord_msg:
                    await old_discord_msg.delete()
                return Result.fail(
                    Error(
                        code=ErrorCode.NO_REACTION_ROLES,
                        message="Нет настроенных реакций для ролей",
                    )
                )

            lines = []
            emojis_to_add = []

            for reaction in all_reactions:
                role = guild.get_role(reaction.role_id)
                if role:
                    lines.append(f"{reaction.emoji} - {role.mention}")
                    emojis_to_add.append(reaction.emoji)
                else:
                    logger.warning(
                        f"Role {reaction.role_id} not found in guild {guild.id}"
                    )
                    await uow.reaction_roles.remove_reaction_role(
                        guild.id, reaction.role_id
                    )
                    logger.debug(
                        f"Removed reaction role {reaction.role_id} ({reaction.emoji})"
                    )

            premsg = "Прожми реакт и получи свою роль мужичочек\n"
            generated_msg = "\n".join(lines)

            if not generated_msg:
                logger.warning("All roles were removed, deleting message")
                if old_discord_msg:
                    try:
                        await old_discord_msg.delete()
                        await uow.role_messages.delete(guild.id)
                    except Exception as e:
                        error = handle_discord_exception(e)
                        logger.error(f"Failed to delete old message: {error}")
                        return Result.fail(error)

                return Result.fail(
                    Error(
                        code=ErrorCode.NO_REACTION_ROLES,
                        message="Все роли были удалены, сообщение удалено",
                    )
                )

            result_msg = premsg + generated_msg

            try:
                if old_discord_msg:
                    await old_discord_msg.edit(content=result_msg)
                    logger.info("Updated discord message")
                    message = old_discord_msg
                    was_created = False
                else:
                    message = await channel.send(result_msg)
                    logger.info(
                        f"Created new role message in channel {message.channel.name}"
                    )
                    await uow.role_messages.create(
                        message_id=message.id,
                        channel_id=channel.id,
                        guild_id=guild.id,
                    )
                    was_created = True
            except Exception as e:
                error = handle_discord_exception(e)
                logger.error(f"Failed to create/update message: {error}")
                return Result.fail(error)

            try:
                added, removed = await self._sync_reactions(message, emojis_to_add)
            except Exception as e:
                error = handle_discord_exception(e)
                logger.error(f"Failed to sync reactions: {error}")
                return Result.fail(error)

            return Result.ok(
                SetupMessageResult(
                    message=RoleMessageDTO(
                        message_id=message.id,
                        channel_id=channel.id,
                        guild_id=guild.id,
                    ),
                    message_url=message.jump_url,
                    reactions_added=added,
                    reactions_removed=removed,
                    was_created=was_created,
                )
            )

    async def resolve_role_from_reaction(
        self, payload: discord.RawReactionActionEvent, guild: discord.Guild
    ) -> discord.Role | None:
        """Находит связь реакция-роль в БД по реакции, поставленной на конкретное сообщение.

        Args:
            payload: объект RawReactionActionEvent, содержащий в себе всю информацию о реакции
            guild: объект дискорд сервера

        Returns:
            Объект дискорд роли, если такая была найдена.
        """
        async with self._uow_factory() as uow:
            role_msg = await uow.role_messages.get_by_guild_id(payload.guild_id)
            if not role_msg:
                return None

            if payload.message_id != role_msg.message_id:
                logger.debug("Reacted on different message (not role message)")
                return None

            emoji_str = self._get_emoji_str(payload.emoji)

            mapped_role = await uow.reaction_roles.get_by_guild_and_emoji(
                payload.guild_id, emoji_str
            )

            if not mapped_role:
                logger.debug(f"No mapped role found for emoji {emoji_str}")
                return None

            discord_role = guild.get_role(mapped_role.role_id)
            return discord_role

    def _map_to_dto(self, model: ReactionRole) -> ReactionRoleDTO:
        return ReactionRoleDTO(
            id=model.id,
            guild_id=model.guild_id,
            emoji=model.emoji,
            role_id=model.role_id,
        )

    async def _fetch_existing_message(
        self, guild: discord.Guild, role_msg: RoleMessage, uow: UnitOfWork
    ) -> discord.Message | None:
        try:
            old_channel = guild.get_channel(role_msg.channel_id)
            if not old_channel:
                return None

            old_discord_msg = await old_channel.fetch_message(role_msg.message_id)
            return old_discord_msg
        except Exception as e:
            logger.error(f"Error while finding old message: {e}")
            await uow.role_messages.delete(role_msg.guild_id)
            logger.info("Old role message deleted from db")
            return None

    async def _sync_reactions(
        self, message: discord.Message, target_emojis: list[str]
    ) -> tuple[list[str], list[str]]:
        added = []
        removed = []

        for emoji in target_emojis:
            try:
                await message.add_reaction(emoji)
                added.append(emoji)
            except Exception as e:
                logger.error(f"Failed to add reaction {emoji}: {e}")

        for reaction in message.reactions:
            if reaction.emoji not in target_emojis:
                logger.debug(
                    f"Deleting non-react-to-role react {reaction.emoji} from msg"
                )
                await message.clear_reaction(reaction.emoji)
                removed.append(str(reaction.emoji))

        return added, removed

    def _get_emoji_str(self, emoji: discord.PartialEmoji) -> str:
        if emoji.id:
            return f"<:{emoji.name}:{emoji.id}>"
        else:
            return str(emoji)

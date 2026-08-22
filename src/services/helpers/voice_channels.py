import discord
from discord import Member

from src.common import Error, ErrorCode, Result
from src.common.discord_errors import handle_discord_exception
from src.config.const import (
    PRIVATE_CATEGORY_NAME,
    TMP_CHANNEL_PREFIX,
)
from src.config.logging_config import get_logger
from src.services.dto.voice_channels import (
    ChannelCleanupResult,
    MoveMembersResult,
    PrivateRoomResult,
    TemporaryRoomAccessResult,
)
from src.utils import find_category_by_name
from src.utils.gen_name_room import generate_name

logger = get_logger(__name__)


class VoiceChannelHelper:
    """Хелпер для работы с голосовыми каналами Discord.

    Предоставляет статические методы для создания приватных комнат,
    управления доступом и очистки временных каналов.
    """

    @staticmethod
    def resolve_members_from_ids(
        guild: discord.Guild, members: list[int]
    ) -> list[Member]:
        """Преобразует список ID участников в объекты Member.

        Args:
            guild: Discord-сервер.
            members: Список ID участников.

        Returns:
            Список объектов Member, найденных на сервере.
        """
        members = set(members)
        member_objects: list[Member] = []
        for member_id in members:
            member = guild.get_member(int(member_id))
            if member:
                member_objects.append(member)
        logger.debug(f"Resolved members: {[member.name for member in member_objects]}")
        return member_objects

    @staticmethod
    async def grant_temporary_room_access(
        member: discord.Member, channel: discord.VoiceChannel
    ) -> Result[TemporaryRoomAccessResult, Error]:
        """Предоставляет участнику доступ к временной приватной комнате.

        Устанавливает права доступа и увеличивает лимит пользователей.

        Args:
            member: Участник Discord.
            channel: Голосовой канал для предоставления доступа.

        Returns:
            Result содержит:
                - Ok(TemporaryRoomAccessResult): DTO с информацией о предоставлении доступа
                - Fail(Error): Ошибка с кодом INVALID_VOICE_CHANNEL или Discord API ошибка
        """
        if channel.category is None or channel.category.name != PRIVATE_CATEGORY_NAME:
            logger.debug(f"Channel {channel.name} is not in private category, skipping")
            return Result.fail(
                Error(
                    code=ErrorCode.INVALID_VOICE_CHANNEL,
                    message="Канал не находится в приватной категории",
                    details={"channel_id": channel.id, "channel_name": channel.name},
                )
            )

        logger.info(f"Granting tmp room access for {member.name} to {channel.name}")

        overwrites = channel.overwrites_for(member)
        if overwrites.view_channel:
            logger.debug(
                f"No need to overwrite channel for {member.name}, they already have access"
            )
            return Result.ok(
                TemporaryRoomAccessResult(
                    member_id=member.id,
                    member_name=member.name,
                    channel_id=channel.id,
                    channel_name=channel.name,
                    was_granted=False,
                )
            )

        logger.debug(f"Changing permissions for {member.name}")
        try:
            await channel.set_permissions(
                member,
                view_channel=True,
                connect=True,
                move_members=True,
                mute_members=True,
                stream=True,
            )
        except Exception as e:
            error = handle_discord_exception(e)
            logger.error(f"Failed to grant tmp room access to {channel.name}: {error}")
            return Result.fail(error)

        new_limit = (
            channel.user_limit + 1 if channel.user_limit else len(channel.members) + 1
        )

        logger.debug(f"Trying to change user limit to {new_limit}...")
        try:
            await channel.edit(user_limit=new_limit)
            logger.debug(f"Successfully changed user limit to {new_limit}")
        except Exception as e:
            error = handle_discord_exception(e)
            logger.error(f"Failed to change user limit: {error}")
            return Result.fail(error)

        logger.info(f"Successfully granted access for {member.name} to {channel.name}")
        return Result.ok(
            TemporaryRoomAccessResult(
                member_id=member.id,
                member_name=member.name,
                channel_id=channel.id,
                channel_name=channel.name,
                was_granted=True,
            )
        )

    @staticmethod
    async def cleanup_empty_temporary_channel(
        channel: discord.VoiceChannel,
    ) -> Result[ChannelCleanupResult, Error]:
        """Удаляет пустой временный голосовой канал.

        Проверяет, что канал находится в приватной категории, пуст и является временным.

        Args:
            channel: Голосовой канал для проверки и удаления.

        Returns:
            Result содержит:
                - Ok(ChannelCleanupResult): DTO удалённого канала
                - Fail(Error): Ошибка с кодом INVALID_VOICE_CHANNEL или Discord API ошибка
        """
        if channel.category is None or channel.category.name != PRIVATE_CATEGORY_NAME:
            logger.debug(f"Channel {channel.name} is not in private category, skipping")
            return Result.fail(
                Error(
                    code=ErrorCode.INVALID_VOICE_CHANNEL,
                    message="Канал не находится в приватной категории",
                )
            )

        if len(channel.members) > 0:
            logger.debug(f"Channel {channel.name} is not empty, skipping")
            return Result.fail(
                Error(code=ErrorCode.INVALID_VOICE_CHANNEL, message="Канал не пуст")
            )

        if TMP_CHANNEL_PREFIX not in channel.name:
            logger.debug(f"Channel {channel.name} is not temporary, skipping")
            return Result.fail(
                Error(
                    code=ErrorCode.INVALID_VOICE_CHANNEL,
                    message="Канал не является временным",
                )
            )

        logger.info(f"Everyone left {channel.name}. Trying to delete...")
        channel_id = channel.id
        channel_name = channel.name

        try:
            await channel.delete()
            logger.info(f"Successfully deleted temporary channel {channel_name}")
            return Result.ok(
                ChannelCleanupResult(channel_id=channel_id, channel_name=channel_name)
            )
        except Exception as e:
            error = handle_discord_exception(e)
            logger.error(f"Failed to delete temporary channel {channel_name}: {error}")
            return Result.fail(error)

    @staticmethod
    async def create_private_voice_channel(
        guild: discord.Guild, members: list[Member]
    ) -> Result[PrivateRoomResult, Error]:
        """Создаёт приватный голосовой канал для указанных участников.

        Создаёт канал в приватной категории с правами доступа только для указанных участников.

        Args:
            guild: Discord-сервер.
            members: Список участников для доступа к каналу.

        Returns:
            Result содержит:
                - Ok(PrivateRoomResult): DTO созданного канала
                - Fail(Error): Ошибка с кодами GUILD_NOT_FOUND, CATEGORY_NOT_FOUND или Discord API ошибка
        """
        logger.debug(f"Trying to create room for {len(members)} members")

        if not guild:
            logger.error("No guild provided")
            return Result.fail(
                Error(
                    code=ErrorCode.GUILD_NOT_FOUND, message="Не найден дискорд сервер"
                )
            )

        category = find_category_by_name(guild, PRIVATE_CATEGORY_NAME)
        if not category:
            logger.error(f"Category {PRIVATE_CATEGORY_NAME} not found")
            return Result.fail(
                Error(
                    code=ErrorCode.CATEGORY_NOT_FOUND,
                    message=f"Категория {PRIVATE_CATEGORY_NAME} не найдена",
                )
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
        }

        for member in members:
            logger.debug(f"Overwriting rights for {member.name} for new voice channel")
            overwrites[member] = discord.PermissionOverwrite(
                view_channel=True,
                connect=True,
                move_members=True,
                mute_members=True,
                stream=True,
            )

        room_name = generate_name()
        try:
            logger.debug("Trying to create temporal voice channel...")
            new_channel = await guild.create_voice_channel(
                room_name,
                reason="sneaky_little_bastardos",
                user_limit=len(members),
                category=category,
                overwrites=overwrites,
                rtc_region="rotterdam",
            )
            logger.info(
                f"Created private channel: {new_channel.name} (ID: {new_channel.id})"
            )

            return Result.ok(
                PrivateRoomResult(
                    channel_id=new_channel.id,
                    channel_name=new_channel.name,
                    channel_mention=new_channel.mention,
                    affected_users=new_channel.user_limit,
                )
            )

        except Exception as e:
            error = handle_discord_exception(e)
            logger.error(f"Failed to create temporal voice channel: {error}")
            return Result.fail(error)

    @staticmethod
    async def move_members_to_voice_channel(
        guild: discord.Guild, members: list[Member], voice_channel_id: int
    ) -> Result[MoveMembersResult, Error]:
        """Перемещает участников в указанный голосовой канал.

        Перемещает только тех участников, которые находятся в голосовом канале
        и не в приватной категории.

        Args:
            guild: Discord-сервер.
            members: Список участников для перемещения.
            voice_channel_id: ID целевого голосового канала.

        Returns:
            Result содержит:
                - Ok(MoveMembersResult): DTO с количеством перемещённых участников
                - Fail(Error): Ошибка с кодом VOICE_CHANNEL_NOT_FOUND
        """
        voice_channel = guild.get_channel(voice_channel_id)

        if not voice_channel or not isinstance(voice_channel, discord.VoiceChannel):
            logger.error(f"Voice channel {voice_channel_id} not found or invalid type")
            return Result.fail(
                Error(
                    code=ErrorCode.VOICE_CHANNEL_NOT_FOUND,
                    message="Не найден голосовой канал",
                    details={"channel_id": voice_channel_id},
                )
            )

        moved_members = 0
        for member in members:
            if (
                member.voice
                and member.voice.channel
                and member.voice.channel.category
                and member.voice.channel.category.name != PRIVATE_CATEGORY_NAME
            ):
                logger.debug(
                    f"Found member {member.name}, trying to move in tmp channel.."
                )
                try:
                    await member.move_to(voice_channel)
                    moved_members += 1
                    logger.debug(
                        f"Successfully moved {member.name} to {voice_channel.name}"
                    )
                except Exception as e:
                    error = handle_discord_exception(e)
                    logger.error(
                        f"Failed to move member {member.name} to {voice_channel.name}: {error}"
                    )

        logger.info(
            f"Moved {moved_members}/{len(members)} members to {voice_channel.name}"
        )
        return Result.ok(
            MoveMembersResult(
                affected_users=moved_members,
                channel_id=voice_channel.id,
                channel_name=voice_channel.name,
            )
        )

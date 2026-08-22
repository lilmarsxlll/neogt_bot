from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models.reaction_role import ReactionRole
from src.database.models.role_message import RoleMessage


class RoleMessageRepository:
    """Класс, ответственный за взаимодействие с сущностью RoleMessage в БД."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_guild_id(self, guild_id: int) -> RoleMessage | None:
        """Получает RoleMessage по guild_id.

        Args:
            guild_id: ID дискорд сервера

        Returns:
              Найденный RoleMessage (или None)
        """
        result = await self._session.execute(
            select(RoleMessage).where(RoleMessage.guild_id == guild_id)
        )
        return result.scalar_one_or_none()

    async def create(
        self, message_id: int, channel_id: int, guild_id: int
    ) -> RoleMessage:
        """Создает RoleMessage.

        Args:
            message_id: ID сообщения дискорд
            channel_id: ID текстового канала
            guild_id: ID дискорд сервера

        Returns:
            Созданный RoleMessage
        """
        role_msg = RoleMessage(
            message_id=message_id,
            channel_id=channel_id,
            guild_id=guild_id,
        )
        self._session.add(role_msg)
        return role_msg

    async def delete(self, guild_id: int) -> None:
        """Удаляет RoleMessage по переданному guild_id (если такой есть).

        Args:
            guild_id: ID дискорд сервера
        """
        role_msg = await self.get_by_guild_id(guild_id)
        if role_msg:
            await self._session.delete(role_msg)


class ReactionRoleRepository:
    """Класс, ответственный за взаимодействие с сущностью связи реакция-роль в БД."""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def add_reaction_role(
        self, guild_id: int, role_id: int, emoji: str
    ) -> ReactionRole:
        """Создает связь ReactionRole.

        Args:
            guild_id: ID дискорд сервера
            role_id: ID роли
            emoji: эмоджик-реакция

        Returns:
            Созданный ReactionRole
        """
        reaction_role = ReactionRole(
            guild_id=guild_id,
            emoji=emoji,
            role_id=role_id,
        )
        self._session.add(reaction_role)
        return reaction_role

    async def get_role_by_role_id(
        self, guild_id: int, role_id: int
    ) -> ReactionRole | None:
        """Находит ReactionRole по role_id и guild_id.

        Args:
            guild_id: ID дискорд сервера
            role_id: ID роли

        Returns:
            Найденный ReactionRole (или None)
        """
        result = await self._session.execute(
            select(ReactionRole).where(
                ReactionRole.guild_id == guild_id, ReactionRole.role_id == role_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_guild_and_emoji(
        self, guild_id: int, emoji: str
    ) -> ReactionRole | None:
        """Находит ReactionRole по role_id и emoji.

        Args:
            guild_id: ID дискорд сервера
            emoji: эмоджик-реакция

        Returns:
            Найденный ReactionRole (или None)
        """
        result = await self._session.execute(
            select(ReactionRole)
            .where(ReactionRole.guild_id == guild_id)
            .where(ReactionRole.emoji == emoji)
        )
        return result.scalar_one_or_none()

    async def get_all_by_guild(self, guild_id: int) -> list[ReactionRole]:
        """Возвращает все связи реакция-роль в определенном дискорд сервере.

        Args:
            guild_id: ID дискорд сервера

        Returns:
            Список всех найденных ReactionRole
        """
        result = await self._session.execute(
            select(ReactionRole)
            .where(ReactionRole.guild_id == guild_id)
            .order_by(ReactionRole.created_at)
        )
        return list(result.scalars().all())

    async def remove_reaction_role(self, guild_id: int, role_id: int) -> None:
        """Удаляет связь реакция-роль (если такая есть).

        Args:
            guild_id: ID дискорд сервера
            role_id: ID роли
        """
        reaction_role = await self.get_role_by_role_id(guild_id, role_id)
        if reaction_role:
            await self._session.delete(reaction_role)

    async def clear_all_by_guild(self, guild_id: int) -> None:
        """Удаляет все связи реакция-роль в определенном дискорд сервере.

        Args:
            guild_id: ID дискорд сервера
        """
        result = await self.get_all_by_guild(guild_id)
        for reaction_role in result:
            await self._session.delete(reaction_role)

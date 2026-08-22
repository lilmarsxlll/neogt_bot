from sqlalchemy.ext.asyncio import AsyncSession

from src.database.engine import async_session_maker
from src.database.repositories.sqlalchemy_impl import (
    ReactionRoleRepository,
    RoleMessageRepository,
)


class UnitOfWork:
    """Класс, ответственный за жизненный цикл сессии БД."""

    def __init__(self):
        self._session: AsyncSession | None = None
        self._role_messages_repo: RoleMessageRepository | None = None
        self._reaction_roles_repo: ReactionRoleRepository | None = None

    async def __aenter__(self) -> "UnitOfWork":
        self._session = async_session_maker()
        await self._session.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

        await self._session.__aexit__(exc_type, exc_val, exc_tb)

    async def commit(self) -> None:
        """Подтверждает изменения, сделанные во время сессии."""
        await self._session.commit()

    async def rollback(self) -> None:
        """Откатывает изменения, сделанные во время сессии."""
        await self._session.rollback()

    async def flush(self) -> None:
        """Синхронизирует состояние сессии с базой данных."""
        await self._session.flush()

    @property
    def role_messages(self) -> RoleMessageRepository:
        if self._role_messages_repo is None:
            self._role_messages_repo = RoleMessageRepository(self._session)
        return self._role_messages_repo

    @property
    def reaction_roles(self) -> ReactionRoleRepository:
        if self._reaction_roles_repo is None:
            self._reaction_roles_repo = ReactionRoleRepository(self._session)
        return self._reaction_roles_repo

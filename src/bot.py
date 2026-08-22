import discord
from discord.ext import commands

from src.config.const import RoleAction
from src.config.logging_config import get_logger, setup_logging
from src.database.unit_of_work import UnitOfWork
from src.discord_modules.event_handlers.member_join import assign_user_role_on_join
from src.discord_modules.event_handlers.reaction_roles.handle_reaction import (
    handle_reaction,
)
from src.discord_modules.event_handlers.voice_state_update import (
    cleanup_empty_tmp_channel,
    grant_tmp_room_access,
)
from src.discord_modules.tree_commands import register_all_commands
from src.services.reaction_role_service import ReactionRoleService
from src.utils.tree_command_utils import parse_tree_commands

setup_logging()

intents = discord.Intents.default()
intents.message_content = True
intents.voice_states = True
intents.members = True
intents.reactions = True


bot = commands.Bot(command_prefix="!", intents=intents)
logger = get_logger(__name__)

bot.reaction_role_service = ReactionRoleService(
    uow_factory=UnitOfWork,
    bot=bot,
)

register_all_commands(bot)


@bot.event
async def on_ready():
    """Discord event handler: бот готов к работе.

    Синхронизирует slash-команды с Discord и выполняет различные post-init действия.
    """
    logger.info("Bot is ready. Starting sync..")

    try:
        # TODO: ПОСЛЕ ДЕПЛОЯ ОБЯЗАТЕЛЬНО УБРАТЬ
        for guild in bot.guilds:
            logger.debug(f"Clearing guild-specific commands for {guild.name}")
            bot.tree.clear_commands(guild=guild)
            await bot.tree.sync(guild=guild)

        sync = await bot.tree.sync()
        logger.info(f"Successfully synced {len(sync)} global commands")
        logger.debug(f"Synchronized commands: {parse_tree_commands(sync)}")

    except Exception as e:
        logger.error(f"Unexpected error during syncing commands: {e}", exc_info=True)


@bot.event
async def on_voice_state_update(
    member: discord.Member, before: discord.VoiceState, after: discord.VoiceState
):
    """Discord event handler: изменение голосового состояния участника.

    Обрабатывает вход/выход из голосовых каналов, управляет временными комнатами.

    Args:
        member: Участник Discord.
        before: Состояние до изменения.
        after: Состояние после изменения.
    """
    logger.debug(f"Voice state updated for {member.name}")
    await cleanup_empty_tmp_channel(before)
    await grant_tmp_room_access(member, after)


@bot.event
async def on_member_join(member: discord.Member):
    """Discord event handler: новый участник присоединился к серверу.

    Args:
        member: Новый участник Discord.
    """
    await assign_user_role_on_join(member)


@bot.event
async def on_error(event, *args, **kwargs):
    """Discord event handler: необработанная ошибка в event handler.

    Args:
        event: Название события.
        *args: Позиционные аргументы события.
        **kwargs: Именованные аргументы события.
    """
    logger.error(
        f"Unhandled error in {event} with args: {args} and kwargs: {kwargs}",
        exc_info=True,
    )


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    """Discord event handler: добавление реакции к сообщению.

    Обрабатывает выдачу ролей по реакциям.

    Args:
        payload: Данные события реакции.
    """
    if payload.user_id == bot.user.id:
        return
    await handle_reaction(
        bot.reaction_role_service,
        payload,
        bot.get_guild(payload.guild_id),
        RoleAction.ADD,
    )


@bot.event
async def on_raw_reaction_remove(payload: discord.RawReactionActionEvent):
    """Discord event handler: удаление реакции с сообщения.

    Обрабатывает удаление ролей по реакциям.

    Args:
        payload: Данные события реакции.
    """
    if payload.user_id == bot.user.id:
        return
    await handle_reaction(
        bot.reaction_role_service,
        payload,
        bot.get_guild(payload.guild_id),
        RoleAction.REMOVE,
    )

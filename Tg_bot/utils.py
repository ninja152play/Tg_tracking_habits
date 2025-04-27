from telebot.types import BotCommand
from Tg_bot.config import DEFAULT_COMMANDS

async def set_default_commands(bot):
    await bot.set_my_commands([
        BotCommand(*i) for i in DEFAULT_COMMANDS]
    )
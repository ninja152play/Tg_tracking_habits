import asyncio
import telebot
from telebot.async_telebot import AsyncTeleBot

from Tg_bot.config import BOT_TOKEN


bot = AsyncTeleBot(BOT_TOKEN)


async def main():
    await bot.polling(non_stop=True)

if __name__ == "__main__":
    asyncio.run(main())


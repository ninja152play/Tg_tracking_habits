import asyncio
from datetime import datetime, time
from telebot.asyncio_storage import StateMemoryStorage
from telebot.async_telebot import AsyncTeleBot

from Tg_bot.config import BOT_TOKEN
from Tg_bot.notifications import get_progress_habit
from Tg_bot.utils import set_default_commands
from Tg_bot.handlers import register_all_handlers

state_storage = StateMemoryStorage()
bot = AsyncTeleBot(BOT_TOKEN, state_storage=state_storage)


async def notification_send():
    notification_data = await get_progress_habit()
    for user in notification_data:
        for tg_id, habits in user.items():
            if habits:
                text = "Привет! Сегодня ты выполнил привычки:\n"
                for habit in habits:
                    text += f"{habit}\n"
                # Отправка уведомления
                await bot.send_message(tg_id, text)


async def notification_loop():
    while True:
        await notification_send()
        # Ожидаем 24 часа до следующего выполнения
        await asyncio.sleep(24 * 60 * 60)


register_all_handlers(bot)


async def main():
    # Запускаем фоновую задачу для уведомлений
    asyncio.create_task(notification_loop())

    await set_default_commands(bot)
    print("Бот запущен. Ожидание сообщений...")
    await bot.infinity_polling()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен")

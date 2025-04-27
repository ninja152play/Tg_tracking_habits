import os
from dotenv import load_dotenv

load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")

DEFAULT_COMMANDS = (
    ("start", "Запустить бота"),
    ("help", "Вывести справку"),
    ("login", "Войти в аккаунт"),
    ("register", "Зарегистрироваться"),
    ("habits", "Список привычек"),
)
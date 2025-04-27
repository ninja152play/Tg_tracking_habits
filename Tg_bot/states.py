from telebot.handler_backends import State, StatesGroup


class UserState(StatesGroup):
    name = State()
    username = State()
    password = State()
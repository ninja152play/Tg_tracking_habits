import requests
from telebot.types import Message, CallbackQuery

from Tg_bot.config import DEFAULT_COMMANDS
from ..buttons import habits_menu

user_states = {}
user_data = {}

async def get_user_info():
    return user_data


def register_handlers(bot):
    async def refresh_token(message: Message):
        request = {'refresh_token': user_data[message.from_user.id]['refresh_token']}
        response = requests.post('http://127.0.0.1:8000/api/refresh-token',json=request)
        if response.status_code == 200:
            response = response.json()
            user_data[message.from_user.id]['access_token'] = response['access_token']
            return True



    @bot.message_handler(commands=['start'])
    async def start(message: Message):
        await bot.send_message(message.chat.id, 'Привет, я бот для отслеживания привычек!\n'
                                                'Введите команду /help для получения информации о том, как пользоваться ботом.\n'
                                                'Если вы уже зарегистрированы, то введите команду /login\n'
                                                'Если вы хотите зарегистрироваться, то введите команду /register')

    @bot.message_handler(commands=['help'])
    async def help(message: Message):
        text = [f'/{command} - {description}' for command, description in DEFAULT_COMMANDS]
        print(user_data)
        await bot.send_message(message.chat.id,  '\n'.join(text))

    @bot.message_handler(commands=['register'])
    async def register(message: Message):
        user_states[message.from_user.id] = "name"
        await bot.send_message(message.chat.id, 'Введите ваше имя:')

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "name")
    async def get_name(message: Message):
        if message.text.isalpha():
            user_states[message.from_user.id] = "username"
            await bot.send_message(message.chat.id, 'Введите ваш логин:')
            user_data[message.from_user.id]= {'name': message.text}
        else:
            await bot.send_message(message.chat.id, 'Имя должно содержать только буквы!')

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "username")
    async def get_username(message: Message):
        user_states[message.from_user.id] = "password"
        await bot.send_message(message.chat.id, 'Введите ваш пароль:')
        user_data[message.from_user.id]['username'] = message.text

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "password")
    async def get_password(message: Message):
        request = {'username': user_data[message.from_user.id]['username'],
                'password': message.text,
                'name': user_data[message.from_user.id]['name'],
                'tg_id': message.from_user.id}
        user_data.pop(message.from_user.id)
        response = requests.post('http://127.0.0.1:8000/api/register',json=request)
        if response.status_code == 200:
            response = response.json()
            user_data[message.from_user.id] = {'access_token': response['access_token']}
            user_data[message.from_user.id]['refresh_token'] = response['refresh_token']
            user_data[message.from_user.id]['token_type'] = response['token_type']
            await bot.send_message(message.chat.id, 'Вы успешно зарегистрировались!')
        elif response.status_code == 400:
            await bot.send_message(message.chat.id, 'Пользователь с таким логином уже существует!')
        elif response.status_code == 409:
            await bot.send_message(message.chat.id, 'Вы уже зарегистрированы!')
        else:
            await bot.send_message(message.chat.id, 'Что-то пошло не так! Попробуйте еще раз!')
        user_states.pop(message.from_user.id)

    @bot.message_handler(commands=['login'])
    async def login(message: Message):
        await bot.send_message(message.chat.id, 'Введите ваш логин:')
        user_states[message.from_user.id] = "login"

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "login")
    async def get_login(message: Message):
        await bot.send_message(message.chat.id, 'Введите ваш пароль:')
        user_data[message.from_user.id] = {'login': message.text}
        user_states[message.from_user.id] = "password_login"

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "password_login")
    async def get_password(message: Message):
        request = {'username': user_data[message.from_user.id]['login'],
                   'password': message.text,
                   'tg_id': message.from_user.id
                   }
        user_data.pop(message.from_user.id)
        response = requests.post('http://127.0.0.1:8000/api/login',json=request)
        if response.status_code == 200:
            response = response.json()
            user_data[message.from_user.id] = {'access_token': response['access_token']}
            user_data[message.from_user.id]['refresh_token'] = response['refresh_token']
            user_data[message.from_user.id]['token_type'] = response['token_type']
            await bot.send_message(message.chat.id, 'Вы успешно авторизовались!')
            user_states.pop(message.from_user.id)
        else:
            await bot.send_message(message.chat.id, 'Неверный логин или пароль!')

    @bot.message_handler(commands=['habits'])
    async def habits(message: Message):
        if not message.from_user.id in user_data or not 'access_token' in user_data[message.from_user.id]:
            await bot.send_message(message.chat.id, 'Вы не авторизованы! Введите команду /login для авторизации или /register для регистрации.')
        else:
            headers = {"Authorization": f'Bearer {user_data[message.from_user.id]["access_token"]}'}
            response = requests.get('http://127.0.0.1:8000/api/habits', headers=headers)
            if response.status_code == 200:
                response = response.json()
                text = 'Ваши привычки:\n\n'
                for habit in response:
                    text += f'Название привычки: {habit["name"]}\nСтатус: {habit["status"]}\n\n'
                else:
                    text += "У вас нет привычек!"
                await bot.send_message(message.chat.id, text, reply_markup=habits_menu())
            elif response.status_code == 401:
                if await refresh_token(message):
                    await habits(message)

    @bot.callback_query_handler(func=lambda call: call.data == "add_habit")
    async def add_habit(callback: CallbackQuery):
        await bot.send_message(callback.message.chat.id, 'Введите название привычки:')
        user_states[callback.from_user.id] = "habit_title"

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "habit_title")
    async def get_habit_title(message: Message):
        user_states.pop(message.from_user.id)
        response = requests.post('http://127.0.0.1:8000/api/habits',
                                 json={'name': message.text},
                                 headers={'Authorization': f'Bearer {user_data[message.from_user.id]["access_token"]}'})
        if response.status_code == 200:
            await bot.send_message(message.chat.id, 'Привычка успешно добавлена! Введите команду /habits для просмотра списка привычек.')
        else:
            await bot.send_message(message.chat.id, 'Что-то пошло не так! Попробуйте еще раз!')

    @bot.callback_query_handler(func=lambda call: call.data == 'edit_habit')
    async def change_habit(callback: CallbackQuery):
        await bot.send_message(callback.message.chat.id, 'Введите название привычки, которую вы хотите изменить:')
        user_states[callback.from_user.id] = "habit_title_edit"

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "habit_title_edit")
    async def get_habit_title(message: Message):
        user_states[message.from_user.id] = "new_habit_title"
        user_data[message.from_user.id]['habit_title'] = message.text
        await bot.send_message(message.chat.id, 'Введите новое название привычки:')

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "new_habit_title")
    async def get_new_habit_title(message: Message):
        user_states.pop(message.from_user.id)
        response = requests.patch('http://127.0.0.1:8000/api/habits',
                                json={'old_title': user_data[message.from_user.id]['habit_title'],
                                'new_title': message.text},
                                headers={'Authorization': f'Bearer {user_data[message.from_user.id]["access_token"]}'})
        if response.status_code == 200:
            await bot.send_message(message.chat.id, 'Привычка успешно изменена! Введите команду /habits для просмотра списка привычек.')
        else:
            await bot.send_message(message.chat.id, 'Что-то пошло не так! Попробуйте еще раз!')

    @bot.callback_query_handler(func=lambda call: call.data == 'edit_habit_status')
    async def change_habit_status(callback: CallbackQuery):
        await bot.send_message(callback.message.chat.id, 'Введите название привычки, статус которой вы хотите изменить:')
        user_states[callback.from_user.id] = "habit_title_status_edit"

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "habit_title_status_edit")
    async def get_habit_title_on_status_edit(message: Message):
        user_states.pop(message.from_user.id)
        response = requests.put('http://127.0.0.1:8000/api/habits',
                                json={'title': message.text},
                                headers={'Authorization': f'Bearer {user_data[message.from_user.id]["access_token"]}'})
        if response.status_code == 200:
            await bot.send_message(message.chat.id, 'Поздравляем! С достижением вашей цели! Введите команду /habits для просмотра списка привычек.')
        else:
            await bot.send_message(message.chat.id, 'Что-то пошло не так! Попробуйте еще раз!')

    @bot.callback_query_handler(func=lambda call: call.data == 'del_habit')
    async def delete_habit(callback: CallbackQuery):
        await bot.send_message(callback.message.chat.id, 'Введите название привычки, которую вы хотите удалить:')
        user_states[callback.from_user.id] = "habit_title_delete"

    @bot.message_handler(func=lambda msg: user_states.get(msg.from_user.id) == "habit_title_delete")
    async def get_habit_title_on_delete(message: Message):
        user_states.pop(message.from_user.id)
        response = requests.delete('http://127.0.0.1:8000/api/habits',
                                json={'title': message.text},
                                headers={'Authorization': f'Bearer {user_data[message.from_user.id]["access_token"]}'})
        if response.status_code == 200:
            await bot.send_message(message.chat.id, 'Привычка успешно удалена! Введите команду /habits для просмотра списка привычек.')
        else:
            await bot.send_message(message.chat.id, 'Что-то пошло не так! Попробуйте еще раз!')
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

def habits_menu():
    menu = InlineKeyboardMarkup(row_width=1)
    menu.add(
        InlineKeyboardButton(text='Добавить привычку', callback_data='add_habit'),
        InlineKeyboardButton(text='Изменить название привычки', callback_data='edit_habit'),
        InlineKeyboardButton(text='Изменить статус привычки', callback_data='edit_habit_status'),
        InlineKeyboardButton(text='Удалить привычку', callback_data='del_habit')
    )
    return menu

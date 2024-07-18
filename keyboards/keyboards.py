from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from database.database import db

#####

button_1 = KeyboardButton(text='Выбрать категории')
button_2 = KeyboardButton(text='Архив')
button_3 = KeyboardButton(text='Обо мне')

user_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                    one_time_keyboard=True,
                                    keyboard=[[button_1],
                                              [button_2],
                                              [button_3]])


#####

button_1 = KeyboardButton(text='Создание нового отложенного сообщения')
button_2 = KeyboardButton(text='Указание категории для рассылки')
button_3 = KeyboardButton(text='Указание времени для рассылки')
button_4 = KeyboardButton(text='Удаление сообщения')
button_5 = KeyboardButton(text='Добавить категорию')
button_6 = KeyboardButton(text='Добавить подкатегорию')

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_1],
              [button_2, button_3],
              [button_4],
              [button_5, button_6]],
    resize_keyboard=True,
    one_time_keyboard=True)


#####

def category_keyboard(user_id) -> ReplyKeyboardMarkup:
    cat_list = db.get_all_categories()
    user_cat_list = db.get_categories_by_user_id(user_id)

    buttons = []

    for cat in cat_list:
        if cat in user_cat_list:
            button_text = f'{cat[1]}✅'
        else:
            button_text = f'{cat[1]}❌'
        buttons.append(KeyboardButton(text=button_text))

    kb_builder = ReplyKeyboardBuilder()
    kb_builder.row(*buttons, width=3)
    return kb_builder.as_markup(resize_keyboard=True)


#####

def all_category_keyboard() -> ReplyKeyboardMarkup:
    cat_list = db.get_all_categories()

    buttons = []

    for cat in cat_list:
        button_text = f'+{cat[1]}'
        buttons.append(KeyboardButton(text=button_text))

    kb_builder = ReplyKeyboardBuilder()
    kb_builder.row(*buttons, width=3)
    return kb_builder.as_markup(resize_keyboard=True)

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

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
button_5 = KeyboardButton(text='Добавление категорий/подкатегорий в бд')

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_1],
              [button_2, button_3],
              [button_4],
              [button_5]],
    resize_keyboard=True,
    one_time_keyboard=True)


#####
cats_list = {
    'news': True, 
    'Спорт': False,
    'Женщины': False,
    'Бизнес': False
}


def category_keyboard() -> ReplyKeyboardMarkup:
    buttons = []
    for category, subscribed in cats_list.items():
        button_text = f'{category}✅' if subscribed else f'{category}❌'
        buttons.append(KeyboardButton(text=button_text))
    kb_builder = ReplyKeyboardBuilder()
    kb_builder.row(*buttons)
    return kb_builder.as_markup(resize_keyboard=True)

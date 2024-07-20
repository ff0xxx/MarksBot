from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from db_handler.db_funk import UserGateway


#####

button_1 = KeyboardButton(text='Выбрать категории')
button_2 = KeyboardButton(text='Архив')

user_keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                                    one_time_keyboard=True,
                                    keyboard=[[button_1],
                                              [button_2]])


#####

button_1 = KeyboardButton(text='Создание сообщения')
button_2 = KeyboardButton(text='Удаление сообщения')
button_3 = KeyboardButton(text='Указание времени для рассылки')
button_4 = KeyboardButton(text='Указание категории для рассылки')
button_5 = KeyboardButton(text='Добавить категорию')
button_6 = KeyboardButton(text='Добавить подкатегорию')
button_7 = KeyboardButton(text='Удалить категорию')
button_8 = KeyboardButton(text='Выбрать категории')

admin_keyboard = ReplyKeyboardMarkup(
    keyboard=[[button_1, button_2],
              [button_3, button_4],
              [button_5, button_6],
              [button_7, button_8]],
    resize_keyboard=True)


#####

async def category_keyboard(user_id, user_gateway: UserGateway) -> ReplyKeyboardMarkup:
    cat_list = await user_gateway.get_all_categories()
    user_cat_list = await user_gateway.get_categories_by_user_id(user_id)

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

async def plus_category_keyboard(user_gateway: UserGateway) -> ReplyKeyboardMarkup:
    cat_list = await user_gateway.get_all_categories()

    buttons = []

    for cat in cat_list:
        button_text = f'+{cat[1]}'
        buttons.append(KeyboardButton(text=button_text))

    kb_builder = ReplyKeyboardBuilder()
    kb_builder.row(*buttons, width=3)
    return kb_builder.as_markup(resize_keyboard=True,
                                one_time_keyboard=True)


async def minus_category_keyboard(user_gateway: UserGateway) -> ReplyKeyboardMarkup:
    """INLINE-КЛАВИАТУРА ДЛЯ УДАЛЕНИЯ КАТЕГОРИЙ"""
    cat_list = await user_gateway.get_all_categories()

    buttons = []

    for cat in cat_list:
        cat_name = cat[1]
        cat_id = await user_gateway.get_cat_id_by_name(cat_name)
        button = InlineKeyboardButton(text=cat_name,
                                      callback_data='-' + str(cat_id['id']))
        buttons.append(button)

    builder = InlineKeyboardBuilder().row(*buttons, width=2)

    return builder.as_markup()

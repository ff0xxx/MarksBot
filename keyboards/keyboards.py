from aiogram.types          import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from db_handler.db_funk     import UserGateway


#####

async def user_keyboard():
    button_1 = KeyboardButton(text='Выбрать категории')
    button_2 = KeyboardButton(text='Архив')

    user_kb = ReplyKeyboardMarkup(resize_keyboard=True,
                                        one_time_keyboard=True,
                                        keyboard=[[button_1],
                                                  [button_2]])

    return user_kb


#####

async def admin_keyboard():
    button_1 = KeyboardButton(text='Добавить пост')
    button_2 = KeyboardButton(text='Удалить пост')
    button_3 = KeyboardButton(text='Добавить категорию')
    button_4 = KeyboardButton(text='Добавить подкатегорию')
    button_5 = KeyboardButton(text='Удалить категорию')
    button_6 = KeyboardButton(text='Выбрать категории')
    button_7 = KeyboardButton(text='Архив')

    admin_kb = ReplyKeyboardMarkup(
        keyboard=[[button_1, button_2],
                  [button_3, button_4],
                  [button_5, button_6],
                  [button_7]],
        resize_keyboard=True)

    return admin_kb


#####

async def category_keyboard(user_id, user_gateway: UserGateway) -> InlineKeyboardMarkup:
    """INLINE-КЛАВИАТУРА ДЛЯ ПОДПИСОК: КАТЕГОРИИ"""
    cat_list = await user_gateway.get_all_categories(with_subcategories=True)
    user_subcats = await user_gateway.get_all_subcategories_by_user_id(user_id=user_id)
    user_subcats_list = [sub['id'] for sub in user_subcats]

    buttons = []
    for cat in cat_list:
        cat_id = await user_gateway.get_cat_id_by_name(name=cat[1])
        cat_subcats = await user_gateway.get_subcats_by_cat_id(cat_id=int(cat_id['id']))
        cat_subcats_list = [sub['id'] for sub in cat_subcats]

        # если пересечения со всеми subcats у subcats текущей подкатегории
        if set(user_subcats_list) & set(cat_subcats_list):
            cat_name = cat[1] + ': ✅'
        else:
            cat_name = cat[1] + ': ❌'

        button = InlineKeyboardButton(text=cat_name,
                                      callback_data='cat' + str(cat_id['id']))
        buttons.append(button)

    builder = InlineKeyboardBuilder().row(*buttons, width=3)

    return builder.as_markup()


#####

async def subcategory_keyboard(user_id, cat_id, user_gateway: UserGateway) -> InlineKeyboardMarkup:
    """INLINE-КЛАВИАТУРА ДЛЯ ПОДПИСОК: ПОДКАТЕГОРИИ"""
    subcat_list = await user_gateway.get_subcats_by_cat_id(cat_id)
    user_subcat_list = await user_gateway.get_subcategories_by_user_id(user_id)

    buttons = []

    for subcat in subcat_list:
        if subcat in user_subcat_list:
            sign = '✅'
        else:
            sign = '❌'

        subcat_name = subcat[1] + ': ' + sign

        button = InlineKeyboardButton(text=subcat_name,
                                      callback_data=f"sub {str(subcat['id'])} {cat_id} {sign}")
        buttons.append(button)

    back_button = InlineKeyboardButton(text='Назад', callback_data='go_back')

    # Если хотя бы на одну категорию ОТПИСАН - одписываюсь на все
    sign_for_all = ('✅', '❌')[any(subcat not in user_subcat_list for subcat in subcat_list)]
    all_cuts_button = InlineKeyboardButton(text='Все', callback_data=f'all {cat_id} {sign_for_all}')

    builder = InlineKeyboardBuilder().row(*buttons, width=3)
    builder.row(back_button, all_cuts_button, width=2)

    return builder.as_markup()

#####

async def all_subcategory_subscribe_keyboard(user_id, cat_id, sign,  user_gateway: UserGateway) -> InlineKeyboardMarkup:
    """INLINE-КЛАВИАТУРА ДЛЯ ПОДПИСОК/ОТПИСОК на все ПОДКАТЕГОРИИ"""
    subcat_list = await user_gateway.get_subcats_by_cat_id(cat_id)

    buttons = []

    if sign == '❌':
        sign = '✅'
        func = user_gateway.subscribe_user_to_category_by_id
    else:
        sign = '❌'
        func = user_gateway.unsubscribe_user_from_category_by_id

    for subcat in subcat_list:
        await func(user_id, int(subcat['id']))
        subcat_name = subcat['name'] + ': ' + sign

        button = InlineKeyboardButton(text=subcat_name,
                                      callback_data=f"sub {str(subcat['id'])} {cat_id} {sign}")
        buttons.append(button)

    back_button = InlineKeyboardButton(text='Назад', callback_data='go_back')
    all_cuts_button = InlineKeyboardButton(text='Все', callback_data=f'all {cat_id} {sign}')

    builder = InlineKeyboardBuilder().row(*buttons, width=3)
    builder.row(back_button, all_cuts_button, width=2)

    return builder.as_markup()

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


#####

async def minus_category_keyboard(user_gateway: UserGateway) -> InlineKeyboardMarkup:
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


#####

async def add_post_category_keyboard(user_gateway: UserGateway) -> InlineKeyboardMarkup:
    """INLINE-КЛАВИАТУРА ДЛЯ ВЫБОРА КАТЕГОРИИ ПОСТА"""
    cat_list = await user_gateway.get_all_categories(with_subcategories=True)

    buttons = []

    for cat in cat_list:
        cat_name = cat[1]
        cat_id = await user_gateway.get_cat_id_by_name(name=cat_name)

        button = InlineKeyboardButton(text=cat_name,
                                      callback_data=f"post_cat {str(cat_id['id'])}")
        buttons.append(button)

    builder = InlineKeyboardBuilder().row(*buttons, width=3)

    return builder.as_markup()


#####

async def add_post_subcategory_keyboard(cat_id, user_gateway: UserGateway) -> InlineKeyboardMarkup:
    """INLINE-КЛАВИАТУРА ВЫБОРА ПОДКАТЕГОРИИ ПОСТА"""
    subcat_list = await user_gateway.get_subcats_by_cat_id(cat_id)

    buttons = []

    for subcat in subcat_list:
        subcat_name = subcat[1]  #+ sign
        subcat_id = subcat['id']

        button = InlineKeyboardButton(text=subcat_name,
                                      callback_data=f"post_sub {str(subcat_id)}")
        buttons.append(button)

    builder = InlineKeyboardBuilder().row(*buttons, width=3)

    return builder.as_markup()


#####

async def post_time_keyboard(user_gateway: UserGateway) -> InlineKeyboardMarkup:
    """INLINE-КЛАВИАТУРА ВЫБОРА ВРЕМЕНИ ПУБЛИКАЦИИ ПОСТА"""
    button_1 = InlineKeyboardButton(text='Сейчас', callback_data='now')
    button_2 = InlineKeyboardButton(text='Свой вариант', callback_data='somewhen')

    return InlineKeyboardMarkup(inline_keyboard=[[button_1],
                                                 [button_2]])

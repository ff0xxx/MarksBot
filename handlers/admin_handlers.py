from aiogram                        import Router, F
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.types                  import Message

from keyboards.keyboards import all_category_keyboard
from lexicon.lexicon_ru             import LEXICON_RU
from config_data.config             import load_config
from database.database              import db

router: Router = Router()


# декоратор для проверки от админа ли пришло сообщение
def is_admin(func):
    async def wrapper(message: Message):
        if message.from_user.id in load_config().tg_bot.admin_ids:  # Замените check_condition на вашу проверку
            print('ADMIN')  # как получить имя функции?
            return func(message)
    return wrapper


@router.message(is_admin(F.text == 'Создание нового отложенного сообщения'))
async def new_post_press(message: Message):
    """admin_keyboard: клик 'Создание нового отложенного сообщения' """
    pass


@router.message(is_admin(F.text == 'Указание категории для рассылки'))
async def cat_new_post_press(message: Message):
    """admin_keyboard: клик 'Указание категории для рассылки' """
    pass


@router.message(is_admin(F.text == 'Указание времени для рассылки'))
async def time_new_post_press(message: Message):
    """admin_keyboard: клик 'Указание времени для рассылки' """
    pass


@router.message(is_admin(F.text == 'Удаление сообщения'))
async def delete_new_post_press(message: Message):
    """admin_keyboard: клик 'Удаление сообщения' """
    await message.reply(text='Удаление сообщения')

select_cat_name = 0
@router.message(is_admin(F.text == 'Добавить категорию'))
async def add_cat_press(message: Message):
    """admin_keyboard: клик 'Добавить категорию' """
    global select_cat_name
    await message.reply(text='Ведите название категории')
    select_cat_name = 1

@router.message(is_admin(select_cat_name == 1))
async def add_cat(message):
    global select_cat_name

    db.add_category(name=message.text)
    await message.reply(text='Вы добавили новую категорию!')

    select_cat_name = 0


select_subcat_name = 0
@router.message(is_admin(F.text == 'Добавить подкатегорию'))
async def add_subcat_press(message: Message):
    """admin_keyboard: клик 'Добавить подкатегорию' """
    global select_subcat_name
    await message.answer(text='Выберите категорию, в которую входит новая подкатегория',
                         reply_markup=all_category_keyboard())
    select_subcat_name = 1

cat_id = None
@router.message(is_admin(lambda message: message.text[0] == '+'))
async def add_cat(message):
    db.get_cat_id_by_name(message.text.lstrip('+'))
    await message.reply(text='Ведите название подкатегории')

@router.message(is_admin(lambda message: (select_subcat_name == 1) and (cat_id is not None)))
async def add_cat(message):
    global select_subcat_name, cat_id

    db.add_subcategory(parent_id=cat_id, name=message.text)
    await message.reply(text='Вы добавили новую подкатегорию!')

    select_subcat_name = 0
    cat_id = None


@router.message()
async def send_echo(message: Message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ НЕОЖИДАННЫХ СООБЩЕНИЙ"""
    await message.reply(text=LEXICON_RU['echo'])
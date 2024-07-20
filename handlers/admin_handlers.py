from aiogram                        import Router, F
from aiogram.types import Message, CallbackQuery
from db_handler.db_funk             import UserGateway
from filters.filters import IsDeleteCatCallbackData
from keyboards.keyboards import plus_category_keyboard, minus_category_keyboard
from lexicon.lexicon_ru             import LEXICON_RU

router: Router = Router()

# FSM ТУТ СТЫД, ДА, ЗНАЮ, ИЗМЕНЮ КАК-НИБУДЬ

@router.message(F.text == 'Создание сообщения')
async def new_post_press(message: Message):
    """admin_keyboard: клик 'Создание нового отложенного сообщения' """
    await message.reply(text='Создание нового отложенного сообщения')


@router.message(F.text == 'Указание категории для рассылки')
async def cat_new_post_press(message: Message):
    """admin_keyboard: клик 'Указание категории для рассылки' """
    await message.reply(text='Указание категории для рассылки')


@router.message(F.text == 'Указание времени для рассылки')
async def time_new_post_press(message: Message):
    """admin_keyboard: клик 'Указание времени для рассылки' """
    await message.reply(text='Указание времени для рассылки')


@router.message(F.text == 'Удаление сообщения')
async def delete_new_post_press(message: Message):
    """admin_keyboard: клик 'Удаление сообщения' """
    await message.reply(text='Удаление сообщения')


@router.message(F.text == 'Удалить категорию')
async def delete_cats_press(message: Message, user_gateway: UserGateway):
    """admin_keyboard: клик 'Удалить категорию' """
    await message.answer(text='Выберите какую категорию удалить',
                         reply_markup=await minus_category_keyboard(user_gateway))


@router.callback_query(IsDeleteCatCallbackData())
async def delete_cat_press(callback: CallbackQuery, user_gateway: UserGateway):
    """minus_category_keyboard: клик"""
    await user_gateway.delete_category(int(callback.data[1:]))
    await callback.answer(text='Вы удалили категорию')


select_cat_name = 0
@router.message(F.text == 'Добавить категорию')
async def add_cat_press(message: Message):
    """admin_keyboard: клик 'Добавить категорию' """
    global select_cat_name
    await message.reply(text='Ведите название категории')
    select_cat_name = 1


def is_select_cat_name_equal(mean) -> bool:
    """Проверяет, равно ли значение select_cat_name 1."""
    global select_cat_name
    return select_cat_name == mean

@router.message(lambda message: is_select_cat_name_equal(1))
async def add_cat(message, user_gateway: UserGateway):
    global select_cat_name

    await user_gateway.add_category(name=message.text)
    await message.reply(text='Вы добавили новую категорию!')

    select_cat_name = 0


select_subcat_name = 0
@router.message(F.text == 'Добавить подкатегорию')
async def add_subcat_press(message: Message, user_gateway):
    """admin_keyboard: клик 'Добавить подкатегорию' """
    global select_subcat_name
    await message.answer(text='Выберите категорию, в которую входит новая подкатегория',
                         reply_markup=await plus_category_keyboard(user_gateway=user_gateway))
    select_subcat_name = 1

cat_id = None
@router.message(lambda message: message.text[0] == '+')
async def add_cat(message, user_gateway: UserGateway):
    global cat_id
    cat_id = await user_gateway.get_cat_id_by_name(message.text.lstrip('+'))
    await message.reply(text='Ведите название подкатегории')

def is_select_subcat_name_equal(mean) -> bool:
    global select_subcat_name
    return select_subcat_name == mean


def is_cat_id_not_None() -> bool:
    global cat_id
    return cat_id is not None

@router.message(lambda message: (is_select_subcat_name_equal(1)) and is_cat_id_not_None())
async def add_cat(message, user_gateway: UserGateway):
    global select_subcat_name, cat_id

    await user_gateway.add_subcategory(parent_id=cat_id['id'], name=message.text)
    await message.reply(text='Вы добавили новую подкатегорию!')

    select_subcat_name = 0
    cat_id = None


@router.message()
async def send_echo(message: Message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ НЕОЖИДАННЫХ СООБЩЕНИЙ"""
    await message.reply(text=LEXICON_RU['echo'])

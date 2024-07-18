from aiogram                import Router, F
from aiogram.types          import Message

from lexicon.lexicon_ru     import LEXICON_RU
from keyboards.keyboards import category_keyboard
from database.database import db

router: Router = Router()


@router.message(F.text == 'Выбрать категории')
async def select_category(message):
    """user_keyboard: клик 'Выбрать категории' """
    await message.answer(text='Выберите категории',
                         reply_markup=category_keyboard(user_id=message.from_user.id))


@router.message(F.text == 'Архив')
async def send_archive(message):
    """user_keyboard: клик 'Архив' """
    await message.reply(text='Выслали последние 10 записей из ваших категорий')


@router.message(F.text == 'Обо мне')
async def process_help_command(message):
    """user_keyboard: клик 'Обо мне' """
    await message.answer(LEXICON_RU['about'])


@router.message(lambda message: message.text.rstrip('✅❌') in [cat[1] for cat in db.get_all_categories()])
async def process_category(message: Message):
    """category_keyboard(): клик """
    user_id = message.from_user.id
    sign = message.text[-1]
    category_name = message.text.rstrip('✅❌')

    if sign == '✅':
        db.unsubscribe_user_from_category(user_id=user_id, category_name=category_name)
        await message.answer(text=f'Вы отписались от категории "{category_name}".',
                             reply_markup=category_keyboard(user_id=user_id))
    elif sign == '❌':
        db.subscribe_user_from_category(user_id=user_id, category_name=category_name)
        await message.answer(text=f'Вы подписались на категорию "{category_name}".',
                             reply_markup=category_keyboard(user_id=user_id))


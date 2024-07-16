from aiogram                import Router, F
from aiogram.types          import Message

from lexicon.lexicon_ru     import LEXICON_RU
from keyboards.keyboards import category_keyboard, cats_list

router: Router = Router()
# ✅❌


@router.message(F.text == 'Выбрать категории')
async def select_category(message):
    """user_keyboard: клик 'Выбрать категории' """
    await message.answer(text='Выберите категории',
                         reply_markup=category_keyboard())


@router.message(F.text == 'Архив')
async def send_archive(message):
    """user_keyboard: клик 'Архив' """
    await message.reply(text='Выслали последние 10 записей из ваших категорий')


@router.message(F.text == 'Обо мне')
async def process_help_command(message):
    """user_keyboard: клик 'Обо мне' """
    await message.answer(LEXICON_RU['about'])


@router.message(lambda message: message.text.rstrip('✅ ❌ ') in cats_list)
async def process_category(message: Message):
    """category_keyboard(): клик """
    category = message.text.rstrip('✅ ❌ ')
    subscribed = cats_list[category]
    cats_list[category] = not subscribed
    # button_text = f'✅ {category}' if not subscribed else f'❌ {category}'
    await message.answer(text=(f'Вы подписались на категорию "{category}".',
                               f'Вы отписались от категории "{category}".')[subscribed],
                         reply_markup=category_keyboard())




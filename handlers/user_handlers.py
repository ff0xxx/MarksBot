from aiogram                import Router, F
from aiogram.types          import Message
from db_handler.db_funk     import UserGateway
from keyboards.keyboards    import category_keyboard
from lexicon.lexicon_ru     import LEXICON_RU


router: Router = Router()


@router.message(F.text == 'Выбрать категории')
async def select_category(message,  user_gateway: UserGateway):
    """user_keyboard: клик 'Выбрать категории' """
    await message.answer(text='Выберите категории',
                         reply_markup=await category_keyboard(user_id=message.from_user.id, user_gateway=user_gateway))


@router.message(F.text == 'Архив')
async def send_archive(message):
    """user_keyboard: клик 'Архив' """
    await message.reply(text='Выслали последние 10 записей из ваших категорий')


@router.message(F.text == 'Обо мне')
async def process_help_command(message):
    """user_keyboard: клик 'Обо мне' """
    await message.answer(LEXICON_RU['about'])


@router.message(lambda message: message.text[-1] in '✅❌')
async def process_category(message: Message, user_gateway: UserGateway):
    """category_keyboard(): клик """
    user_id = message.from_user.id
    sign = message.text[-1]
    category_name = message.text.rstrip('✅❌')

    if sign == '✅':
        await user_gateway.unsubscribe_user_from_category(user_id=user_id, category_name=category_name)
        await message.answer(text=f'Вы отписались от категории "{category_name}".',
                             reply_markup=await category_keyboard(user_id=user_id, user_gateway=user_gateway))
    elif sign == '❌':
        await user_gateway.subscribe_user_to_category(user_id=user_id, category_name=category_name)
        await message.answer(text=f'Вы подписались на категорию "{category_name}".',
                             reply_markup=await category_keyboard(user_id=user_id, user_gateway=user_gateway))

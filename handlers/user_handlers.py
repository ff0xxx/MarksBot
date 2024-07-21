from aiogram                import Router, F
from aiogram.types          import CallbackQuery
from db_handler.db_funk     import UserGateway
from filters.filters        import SelectCategoryCallbackData, SelectSubcategoryCallbackData
from keyboards.keyboards    import category_keyboard, subcategory_keyboard
from lexicon.lexicon_ru     import LEXICON_RU


router: Router = Router()


@router.message(F.text == 'Выбрать категории')
async def select_category(message,  user_gateway: UserGateway):
    """user_keyboard: клик 'Выбрать категории' """
    await message.answer(text='Выберите категории',
                         reply_markup=await category_keyboard(user_id=message.from_user.id, user_gateway=user_gateway))


@router.callback_query(SelectCategoryCallbackData())
async def select_subcategory(callback: CallbackQuery, user_gateway: UserGateway):
    """category_keyboard: клик"""
    await callback.message.edit_text(text='Выберите подкатегории:',
                                     reply_markup=await subcategory_keyboard(user_id=callback.from_user.id,
                                                                             cat_id=int(callback.data[3:]),
                                                                             user_gateway=user_gateway)
                                     )

@router.callback_query(SelectSubcategoryCallbackData())
async def change_subcategory_kb(callback: CallbackQuery, user_gateway: UserGateway):
    """subcategory_keyboard: клик"""
    user_id = callback.from_user.id
    sign = callback.data.split()[3]
    subcat_id = int(callback.data.split()[1])
    parent_id = int(callback.data.split()[2])

    if sign == '✅':
        await user_gateway.unsubscribe_user_from_category_by_id(user_id=user_id, cat_id=subcat_id)
        await callback.message.edit_text(text='Выберите подкатегории:',
                                         reply_markup=await subcategory_keyboard(user_id=user_id,
                                                                                 cat_id=parent_id,
                                                                                 user_gateway=user_gateway))
    elif sign == '❌':
        await user_gateway.subscribe_user_to_category_by_id(user_id=user_id, cat_id=subcat_id)
        await callback.message.edit_text(text='Выберите подкатегории:',
                                         reply_markup=await subcategory_keyboard(user_id=user_id,
                                                                                 cat_id=parent_id,
                                                                                 user_gateway=user_gateway))


@router.message(F.text == 'Архив')
async def send_archive(message):
    """user_keyboard: клик 'Архив' """
    await message.reply(text='Выслали последние 10 записей из ваших категорий')


@router.message(F.text == 'Обо мне')
async def process_help_command(message):
    """user_keyboard: клик 'Обо мне' """
    await message.answer(LEXICON_RU['about'])

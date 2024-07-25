from aiogram                    import Router, F, Bot
from aiogram.filters            import StateFilter
from aiogram.fsm.context        import FSMContext
from aiogram.types              import CallbackQuery
from db_handler.db_funk         import UserGateway
from filters.callback_filters   import (SelectCategoryCallbackData, SelectSubcategoryCallbackData,
                                        SelectPostCatCallbackData, SelectPostSubcatCallbackData)
from filters.message_filters    import IsCorrectArchiveCount
from keyboards.keyboards        import (category_keyboard, subcategory_keyboard,
                                        add_post_category_keyboard, add_post_subcategory_keyboard)
from lexicon.lexicon_ru         import LEXICON_RU
from states.my_states           import FSMArchive

router: Router = Router()


@router.callback_query(F.data == 'go_back')
async def select_category(callback,  user_gateway: UserGateway):
    """category_keyboard: клик 'Назад' """
    user_id = callback.from_user.id
    await callback.message.edit_text(text='Выберите категории',
                                     reply_markup=await category_keyboard(user_id=user_id, user_gateway=user_gateway))


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


##### ARCHIVE

@router.message(F.text == 'Архив')
async def archive_press(message, state: FSMContext, user_gateway: UserGateway):
    """user_keyboard: клик 'Архив' """
    await message.answer(text='Архив какой категории вас интересует?',
                         reply_markup=await add_post_category_keyboard(user_gateway))
    await state.set_state(FSMArchive.select_archive_cat)


@router.callback_query(StateFilter(FSMArchive.select_archive_cat), SelectPostCatCallbackData())
async def get_archive_cat(callback, state: FSMContext, user_gateway: UserGateway):
    cat_id = int(callback.data.split()[1])
    await callback.message.edit_text(text='Конктретнее: архив какой <b>подкатегории</b> вас интересует?',
                                     reply_markup=await add_post_subcategory_keyboard(cat_id, user_gateway))
    await state.set_state(FSMArchive.select_archive_subcat)


@router.callback_query(StateFilter(FSMArchive.select_archive_subcat), SelectPostSubcatCallbackData())
async def get_archive_subcat(callback, state: FSMContext, user_gateway: UserGateway):
    subcat_id = int(callback.data.split()[1])
    await state.update_data(subcat_id=subcat_id)
    await callback.message.delete()
    await callback.message.answer(text='Введите количество последних записей, которые хотите увидеть\n'
                                       'Максимальное количество - 5')
    await state.set_state(FSMArchive.fill_archive_deep)


@router.message(StateFilter(FSMArchive.fill_archive_deep), IsCorrectArchiveCount())
async def correct_send_archive(message, state: FSMContext, user_gateway: UserGateway, bot: Bot):
    user_id = int(message.from_user.id)
    count = int(message.text)
    data = await state.get_data()
    subcat_id = int(data['subcat_id'])

    posts = await user_gateway.get_archive_posts(user_id, subcat_id, count)

    await message.answer(text=f'Вам будет предоставлено {len(posts)} из {count} постов:')
    await user_gateway.send_archive(bot, posts, user_id)

    await state.clear()


@router.message(StateFilter(FSMArchive.fill_archive_deep))
async def incorrect_send_archive(message):
    await message.reply('Пожалуйста, введите число до 5.')


@router.message(F.text == 'Обо мне')
async def process_help_command(message):
    """user_keyboard: клик 'Обо мне' """
    await message.answer(LEXICON_RU['about'])

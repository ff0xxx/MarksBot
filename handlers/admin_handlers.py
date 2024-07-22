from aiogram                        import Router, F
from aiogram.filters                import StateFilter
from aiogram.fsm.context            import FSMContext
from aiogram.types                  import CallbackQuery
from db_handler.db_funk             import UserGateway
from filters.callback_filters       import IsDeleteCatCallbackData, SelectPostCatCallbackData, SelectPostSubcatCallbackData
from filters.message_filters        import IsCorrectPostTime
from keyboards.keyboards            import plus_category_keyboard, minus_category_keyboard, add_post_category_keyboard, \
    add_post_subcategory_keyboard, post_time_keyboard, admin_keyboard
from lexicon.lexicon_ru             import LEXICON_RU
from states.my_states               import FSMFillForm, FSMAddCut
from datetime                       import datetime

router: Router = Router()


@router.message(F.text == 'Добавить пост')
async def new_post_press(message, user_gateway: UserGateway):
    """admin_keyboard: клик 'Добавить пост' """
    await message.reply(text='Выберите категорию поста:',
                        reply_markup=await add_post_category_keyboard(user_gateway))


@router.callback_query(SelectPostCatCallbackData())
async def cat_new_post_press(callback: CallbackQuery, state: FSMContext, user_gateway: UserGateway):
    """add_post_category_keyboard: клик"""
    cat_id = int(callback.data.split()[1])
    await callback.message.edit_text(text='Выберите подкатегорию:',
                                     reply_markup=await add_post_subcategory_keyboard(cat_id, user_gateway))
    await state.set_state(FSMFillForm.fill_post_content)


@router.callback_query(StateFilter(FSMFillForm.fill_post_content),  SelectPostSubcatCallbackData())
async def subcat_new_post_press(callback: CallbackQuery, state: FSMContext, user_gateway: UserGateway):
    """add_post_subcategory_keyboard: клик"""
    subcat_id = int(callback.data.split()[1])

    # state было введено в этом хендлере для этого
    await state.update_data(post_subcat_id=subcat_id)

    await callback.message.delete()
    await callback.message.answer(text='Введите содержимое поста')


@router.message(StateFilter(FSMFillForm.fill_post_content))
async def post_content_sent(message, state: FSMContext, user_gateway: UserGateway):
    # Cохраняем введенное имя в хранилище по ключу "content"
    await state.update_data(post_content=message.text)

    await message.answer(text='Теперь введите время публикации поста',
                         reply_markup=await post_time_keyboard(user_gateway))
    await state.set_state(FSMFillForm.fill_post_sheduled_at)


@router.callback_query(StateFilter(FSMFillForm.fill_post_sheduled_at), F.data.in_(['now', 'somewhen']))
async def post_time_press(callback: CallbackQuery, state: FSMContext, user_gateway: UserGateway):
    await callback.message.delete()

    if callback.data == 'now':
        current_time = datetime.now()
        await state.update_data(post_sheduled_at=current_time)

        # Добавляем это в бд, ибо данных достаточно
        post_data = await state.get_data()
        await user_gateway.add_post(category_id=post_data['post_subcat_id'],
                                    content=post_data['post_content'],
                                    scheduled_at=post_data['post_sheduled_at'])

        await callback.message.edit_text(text='Отлично, вы добавили пост в базу данных!\n'
                                              'Он выйдет в назначенное вами время',
                                         reply_markup=await admin_keyboard())

    elif callback.data == 'somewhen':
        await callback.message.answer(text='Введите свое время выхода поста в формате:\n'
                                           'YYYY:MM:DD hh:mm\n\n'
                                           'Например: 2024.08.06 15:30')


@router.message(StateFilter(FSMFillForm.fill_post_sheduled_at), IsCorrectPostTime())
async def post_correct_time_sent(message, state: FSMContext, user_gateway: UserGateway):
    """Если ввели корректное время"""
    time: str = message.text + ':00.000001'
    input_format = "%Y.%m.%d %H:%M:%S.%f"
    # Преобразуем строку в объект datetime
    entered_time = datetime.strptime(time, input_format)

    await state.update_data(post_sheduled_at=entered_time)

    # Добавляем это в бд, ибо данных достаточно
    post_data = await state.get_data()
    await user_gateway.add_post(category_id=post_data['post_subcat_id'],
                                content=post_data['post_content'],
                                scheduled_at=post_data['post_sheduled_at'])

    await message.answer(text='Отлично, вы добавили пост в базу данных!\n'
                              'Он выйдет в назначенное вами время',
                         reply_markup=await admin_keyboard())

    await state.clear()


@router.message(StateFilter(FSMFillForm.fill_post_sheduled_at))
async def post_incorrect_time_sent(message, state: FSMContext, user_gateway: UserGateway):
    """Если ввели некорректное время"""
    await message.answer(text='Введите корректное время.')


@router.message(F.text == 'Удалить пост')
async def delete_new_post_press(message):
    """admin_keyboard: клик 'Удалить пост' """
    await message.reply(text='Удалить пост')


##### КАТЕГОРИИ

@router.message(F.text == 'Удалить категорию')
async def delete_cats_press(message, user_gateway: UserGateway):
    """admin_keyboard: клик 'Удалить категорию' """
    await message.answer(text='Выберите какую категорию удалить',
                         reply_markup=await minus_category_keyboard(user_gateway))


@router.callback_query(IsDeleteCatCallbackData())
async def delete_cat_press(callback: CallbackQuery, user_gateway: UserGateway):
    """minus_category_keyboard: клик"""
    await user_gateway.delete_category(int(callback.data[1:]))
    await callback.message.delete()
    await callback.message.answer(text='Вы удалили категорию')


@router.message(F.text == 'Добавить категорию')
async def add_cat_press(message, state: FSMContext):
    """admin_keyboard: клик 'Добавить категорию' """
    await message.reply(text='Ведите название категории')

    await state.set_state(FSMAddCut.select_cat_name)


@router.message(StateFilter(FSMAddCut.select_cat_name))
async def add_cat(message, state: FSMContext, user_gateway: UserGateway):
    await user_gateway.add_category(name=message.text)

    await message.answer(text='Вы добавили новую категорию!',
                         reply_markup=await admin_keyboard())
    await state.clear()


@router.message(F.text == 'Добавить подкатегорию')
async def add_subcat_press(message, state: FSMContext, user_gateway: UserGateway):
    """admin_keyboard: клик 'Добавить подкатегорию' """
    await message.answer(text='Выберите категорию, в которую входит новая подкатегория',
                         reply_markup=await plus_category_keyboard(user_gateway=user_gateway))

    await state.set_state(FSMAddCut.select_cat_for_subcat)


@router.message(lambda message: message.text[0] == '+', StateFilter(FSMAddCut.select_cat_for_subcat))
async def add_cat(message, state: FSMContext, user_gateway: UserGateway):
    cat_id = await user_gateway.get_cat_id_by_name(message.text.lstrip('+'))
    await state.update_data(cat_id=int(cat_id['id']))

    await message.reply(text='Ведите название подкатегории')

    await state.set_state(FSMAddCut.select_subcat_name)


@router.message(StateFilter(FSMAddCut.select_subcat_name))
async def add_cat(message, state: FSMContext, user_gateway: UserGateway):
    data = await state.get_data()
    await user_gateway.add_subcategory(parent_id=data['cat_id'], name=message.text)

    await message.answer(text='Вы добавили новую подкатегорию!',
                         reply_markup=await admin_keyboard())

    await state.clear()


@router.message()
async def send_echo(message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ НЕОЖИДАННЫХ СООБЩЕНИЙ"""
    await message.reply(text=LEXICON_RU['echo'])

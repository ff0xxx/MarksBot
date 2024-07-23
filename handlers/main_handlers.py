from aiogram                import Router
from aiogram.fsm.context import FSMContext
from aiogram.types          import Message
from config_data.config     import load_config
from keyboards.keyboards    import admin_keyboard, user_keyboard
from lexicon.lexicon_ru     import LEXICON_RU
from db_handler.db_funk     import UserGateway
from aiogram.filters import Command, StateFilter
from aiogram.fsm.state import default_state

router: Router = Router()


@router.message(Command(commands=['start']), StateFilter(default_state))
async def process_start_command(message: Message, user_gateway: UserGateway):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ КОМАНДЫ '\\start'"""

    await user_gateway.create_tables()

    user_id = message.from_user.id
    await user_gateway.add_user(user_id)

    if user_id in load_config().tg_bot.admin_ids:  # зач запись админа в бд? хотя мб его понизят и ..?
        await message.answer(
            text=LEXICON_RU['/start_admin'],
        )
    else:
        await message.answer(
            text=LEXICON_RU['/start'],
        )


@router.message(Command(commands=['menu']))
async def process_menu_command(message: Message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ КОМАНДЫ '\\menu'"""
    if message.from_user.id in load_config().tg_bot.admin_ids:
        await message.answer(
            text='Вы перешли в админское меню',
            reply_markup=await admin_keyboard()
        )
    else:
        await message.answer(
            text='Вы перешли в меню',
            reply_markup=await user_keyboard()
        )


@router.message(Command(commands=['about']))
async def process_about_command(message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ КОМАНДЫ '\\about'"""
    await message.answer(LEXICON_RU['/about'])


@router.message(Command(commands='cancel'), StateFilter(default_state))
async def process_cancel_command(message: Message):
    """Этот хэндлер будет срабатывать на команду "/cancel" в состоянии
       по умолчанию и сообщать, что эта команда работает внутри машины состояний"""
    await message.answer(
        text='Отменять нечего. Вы вне машины состояний'
    )


@router.message(Command(commands='cancel'), ~StateFilter(default_state))
async def process_cancel_command_state(message: Message, state: FSMContext):
    """Этот хэндлер будет срабатывать на команду "/cancel" в любых состояниях,
       кроме состояния по умолчанию, и отключать машину состояний"""
    await message.answer(
        text='Вы вышли из машины состояний'
    )
    # Сбрасываем состояние и очищаем данные, полученные внутри состояний
    await state.clear()


@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ КОМАНДЫ '\\help'"""
    await message.answer(LEXICON_RU['/help'])


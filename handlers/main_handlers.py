from aiogram import Router
from aiogram.filters        import Command
from aiogram.types          import Message

from config_data.config     import load_config
from keyboards.keyboards    import admin_keyboard, user_keyboard
from lexicon.lexicon_ru     import LEXICON_RU
from database.database      import db

router: Router = Router()


@router.message(Command(commands=['start']))
async def process_start_command(message: Message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ КОМАНДЫ '\\start'"""

    user_id = message.from_user.id
    db.add_user(user_id)

    if user_id in load_config().tg_bot.admin_ids:  # зач запись админа в бд? хотя мб его понизят и ..?
        await message.answer(
            text=LEXICON_RU['/start_admin'],
            reply_markup=admin_keyboard
        )
    else:
        await message.answer(
            text=LEXICON_RU['/start'],
            reply_markup=user_keyboard
        )


@router.message(Command(commands=['help']))
async def process_help_command(message: Message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ КОМАНДЫ '\\help'"""
    await message.answer(LEXICON_RU['/help'])


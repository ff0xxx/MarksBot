from aiogram import Router, F
from aiogram.dispatcher.event.bases import CancelHandler
from aiogram.types          import Message

from lexicon.lexicon_ru     import LEXICON_RU
from config_data.config import load_config

router: Router = Router()


def is_admin(func):
    async def wrapper(message: Message):
        if message.from_user.id not in load_config().tg_bot.admin_ids:  # Замените check_condition на вашу проверку
            await message.reply("Access is denied")
            raise CancelHandler()
        # Если проверка прошла успешно, вызывается оригинальный хендлер
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
    pass


@router.message(is_admin(F.text == 'Добавление категорий/подкатегорий в бд'))
async def add_cat_press(message: Message):
    """admin_keyboard: клик 'Добавление категорий/подкатегорий в бд' """
    pass



@router.message()
async def send_echo(message: Message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ НЕОЖИДАННЫХ СООБЩЕНИЙ"""
    await message.reply(text=LEXICON_RU['echo'])
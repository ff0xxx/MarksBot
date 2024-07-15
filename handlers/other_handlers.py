import logging
import aiogram.exceptions
from aiogram                import Router
from aiogram.types          import Message
from lexicon.lexicon_ru     import LEXICON_RU

logger = logging.getLogger(__name__)
router: Router = Router()


@router.message()
async def send_echo(message: Message):
    """ХЭНДЛЕР ДЛЯ ОБРАБОТКИ НЕОЖИДАННЫХ СООБЩЕНИЙ"""
    logger.debug("Вошли в эхо-хендлер")
    try:
        await message.reply(text=LEXICON_RU['echo'])
        await message.send_copy(chat_id=message.chat.id)
    except TypeError:
        await message.reply(text=LEXICON_RU['no_echo'])
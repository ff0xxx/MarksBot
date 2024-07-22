from typing import Any, Awaitable, Callable, Dict
from aiogram.types import TelegramObject
from aiogram import BaseMiddleware
from config_data.config import load_config
from lexicon.lexicon_ru import LEXICON_RU


class AdminMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self, handler, event, data):

        # Проверяем, является ли пользователь администратором
        if event.from_user.id in load_config().tg_bot.admin_ids:
            result = await handler(event, data)  # Используем await для асинхронного вызова
            return result
        else:
            await event.answer(text=LEXICON_RU['echo'])
            return None

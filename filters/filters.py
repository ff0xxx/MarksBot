from aiogram.filters import BaseFilter
from aiogram.types      import CallbackQuery


class IsDeleteCatCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        try:
            return callback.data[0] == '-'
        except Exception as e:
            return False

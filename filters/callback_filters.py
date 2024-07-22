from aiogram.filters    import BaseFilter
from aiogram.types      import CallbackQuery


class IsDeleteCatCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        try:
            return callback.data[0] == '-'
        except:
            return False


class SelectCategoryCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            return callback.data[:3] == 'cat'
        except:
            return False


class SelectSubcategoryCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            return callback.data.split()[0] == 'sub'
        except:
            return False

class SelectPostCatCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            return callback.data.split()[0] == 'post_cat'
        except:
            return False


class SelectPostSubcatCallbackData(BaseFilter):
    async def __call__(self, callback: CallbackQuery):
        try:
            return callback.data.split()[0] == 'post_sub'
        except:
            return False

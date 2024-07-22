from aiogram.filters    import BaseFilter
from aiogram.types      import Message
from datetime           import datetime


class IsCorrectPostTime(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        user_input = message.text
        date_format = "%Y.%m.%d %H:%M"

        try:
            # Пытаемся распарсить введенную дату
            user_date = datetime.strptime(user_input, date_format)
        except ValueError:
            # Если формат неверный, возвращаем False
            print(ValueError)
            return False

        # Получаем текущее время
        current_time = datetime.now()

        # Проверяем, что введенная дата больше текущей
        return user_date > current_time

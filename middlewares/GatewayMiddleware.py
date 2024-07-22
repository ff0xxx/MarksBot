from aiogram import BaseMiddleware
from db_handler.db_funk import UserGateway


class GatewayMiddleware(BaseMiddleware):
    """
    Middleware для интеграции с базой данных через UserGateway.

    Этот класс предназначен для создания соединения с пулом соединений базы данных
    и предоставления экземпляра UserGateway для обработки данных пользователя
    в обработчиках событий бота.

    Attributes:
        pool: Пул соединений с базой данных, используемый для получения соединений.
    """

    def __init__(self, pool):
        """
        Инициализирует GatewayMiddleware.

        Args:
            pool: Пул соединений с базой данных (например, asyncpg.Pool).
        """
        super().__init__()
        self.pool = pool

    async def __call__(self, handler, event, data):
        """
        Вызывается при каждом событии, обрабатываемом ботом.

        Создает соединение с базой данных и добавляет экземпляр UserGateway
        в словарь data, который затем может быть использован в обработчиках.

        Args:
            handler: Обработчик события, который будет вызван.
            event: Событие, которое обрабатывается.
            data: Словарь, содержащий данные, переданные в обработчик.

        Returns:
            Результат выполнения обработчика события.
        """
        async with self.pool.acquire() as conn:
            data['user_gateway'] = UserGateway(conn)
            return await handler(event, data)

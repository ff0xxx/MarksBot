from aiogram import BaseMiddleware
from db_handler.db_funk import UserGateway


class GatewayMiddleware(BaseMiddleware):
    def __init__(self, pool):
        super().__init__()
        self.pool = pool

    async def __call__(self, handler, event, data):
        async with self.pool.acquire() as conn:
            data['user_gateway'] = UserGateway(conn)
            return await handler(event, data)

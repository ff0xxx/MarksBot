import asyncio
import logging
import asyncpg
from config_data.config                 import load_config
from create_bot                         import bot, dp, admins
from keyboards.set_menu                 import set_main_menu
from handlers                           import main_handlers, user_handlers, admin_handlers
from middlewares.GatewayMiddleware      import GatewayMiddleware
from middlewares.admin_middleware       import AdminMiddleware

from apscheduler.schedulers.asyncio     import AsyncIOScheduler
from middlewares.ApschedulerMiddleware  import SchedulerMiddleware

# Функция, которая выполнится когда бот запустится
async def start_bot():
    await set_main_menu(bot)
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, f'Бот запущен\n'
                                             f'На всякий случай отправьте /start')
    except:
        pass


# Функция, которая выполнится когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен')
    except:
        pass


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] %(name)s %(message)s'
    )

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")

    # регистрация функций при старте и завершении работы бота
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    # Сначала добавляем мидлвары
    admin_handlers.router.message.middleware(AdminMiddleware())
    admin_handlers.router.callback_query.middleware(AdminMiddleware())

    # Затем добавляем маршрутизаторы
    dp.include_router(main_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)

    scheduler.start()

    async with asyncpg.create_pool(dsn=load_config().tg_bot.dsn) as pool:
        dp.update.middleware.register(SchedulerMiddleware(scheduler=scheduler))

        gateway_middleware = GatewayMiddleware(pool)
        dp.message.middleware(gateway_middleware)
        dp.callback_query.middleware(gateway_middleware)

        try:
            await bot.delete_webhook(drop_pending_updates=True)
            logger.info('Starting bot')
            await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
        finally:
            await bot.session.close()


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    asyncio.run(main())

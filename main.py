import logging
import asyncio
from aiogram                import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums          import ParseMode
from config_data.config     import Config, load_config
from handlers import main_handlers, user_handlers, admin_handlers

logger = logging.getLogger(__name__)


async def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] %(name)s %(message)s'
    )

    config: Config = load_config()

    default_properties = DefaultBotProperties(parse_mode=ParseMode.HTML)

    bot = Bot(token=config.tg_bot.token, default=default_properties)
    dp = Dispatcher()

    dp.include_router(main_handlers.router)
    dp.include_router(user_handlers.router)
    dp.include_router(admin_handlers.router)

    logger.info('Starting bot')

    await bot.delete_webhook(drop_pending_updates=True)  # delete updates
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
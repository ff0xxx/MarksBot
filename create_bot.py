from aiogram                    import Bot, Dispatcher
from aiogram.client.default     import DefaultBotProperties
from aiogram.enums              import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from asyncpg_lite               import DatabaseManager
from config_data.config         import load_config

admins = load_config().tg_bot.admin_ids

# инициируем объект, который будет отвечать за взаимодействие с базой данных
db_manager = DatabaseManager(db_url=load_config().tg_bot.dsn, deletion_password=load_config().tg_bot.deletion_psw)

bot = Bot(token=load_config().tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage = MemoryStorage()

# инициируем объект бота
dp = Dispatcher(storage=storage)

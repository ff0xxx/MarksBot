from aiogram import Bot, Dispatcher
from asyncpg_lite import DatabaseManager
from config_data.config import load_config

# получаем список администраторов из .env
admins = load_config().tg_bot.admin_ids

# инициируем объект, который будет отвечать за взаимодействие с базой данных
db_manager = DatabaseManager(db_url=load_config().tg_bot.dsn, deletion_password=load_config().tg_bot.deletion_psw)

# инициируем объект бота, передавая ему parse_mode=ParseMode.HTML по умолчанию
bot = Bot(token=load_config().tg_bot.token) #, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# инициируем объект бота
dp = Dispatcher()

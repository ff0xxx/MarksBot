import asyncpg
import asyncio
from config_data.config import load_config

DSN = load_config().tg_bot.dsn

# ЗНАЮ - ОЧЕНЬ ПЛОХО, СЛЕД КОММИТ БУДЕТ ПОСВЯЩЕН ЭТОМУ ФАЙЛУ!!

async def create_tables():
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY
                )
            """)

            await conn.execute("""
                 CREATE TABLE IF NOT EXISTS categories (
                    id SERIAL PRIMARY KEY,
                    parent_id BIGINT,
                    level BIGINT,
                    name TEXT UNIQUE
                )
            """)
            # Добавление категории "news"
            await conn.execute("""
                            INSERT INTO categories (level, name) VALUES ($1, $2)
                            ON CONFLICT (name) DO NOTHING
                            """, 1, "news")

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS posts (
                    id SERIAL PRIMARY KEY,
                    content TEXT,
                    category_id BIGINT,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    scheduled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
                    CHECK (scheduled_at >= created_at)
                )
            """)

            await conn.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    category_id BIGINT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id),
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)


async def func():
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO categories (level, name) VALUES ($1, $2)
                ON CONFLICT (name) DO NOTHING
            """, 1, "news")


#### FUNCTIONS

async def add_user(user_id):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Проверяем, существует ли пользователь
            user_exists = await conn.fetchrow("SELECT 1 FROM users WHERE user_id = $1", user_id)

            if not user_exists:
                # Вставляем нового пользователя
                await conn.execute("INSERT INTO users (user_id) VALUES ($1)", user_id)
                # Добавляем подписку на категорию "news"
                await add_subscription(user_id, 1)


async def add_category(name):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Вставляем новую категорию
            await conn.execute(
                "INSERT INTO categories (parent_id, level, name) VALUES ($1, $2, $3)",
                None,  # parent_id
                1,     # level
                name
            )


async def add_subcategory(parent_id, name):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Вставляем новую подкатегорию
            await conn.execute(
                "INSERT INTO categories (parent_id, level, name) VALUES ($1, $2, $3)",
                parent_id,
                2,  # level
                name
            )


async def add_post(content, category_id, scheduled_at):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Вставляем новый пост
            await conn.execute(
                "INSERT INTO Posts (content, category_id, scheduled_at) VALUES ($1, $2, $3)",
                content,
                category_id,
                scheduled_at  # scheduled_at должен быть типа datetime
            )


async def add_subscription(user_id, category_id):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Вставляем новую подписку
            await conn.execute(
                "INSERT INTO Subscriptions (user_id, category_id) VALUES ($1, $2)",
                user_id,
                category_id
            )


##### CATEGORY

async def get_cat_id_by_name(name):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Получаем id категории по ее названию
            return await conn.fetchrow(
                'SELECT id FROM categories WHERE name = $1',
                name
            )


async def get_all_categories():
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Получаем все категории, а не подкатегории
            return await conn.fetch(
                'SELECT id, name FROM categories WHERE level = 1'
            )


async def get_categories_by_user_id(user_id):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Получаем категории по id пользователя
            return await conn.fetch(
                """
                SELECT c.id, c.name
                FROM Subscriptions s
                JOIN categories c ON s.category_id = c.id
                WHERE s.user_id = $1
                """,
                user_id
            )


async def unsubscribe_user_from_category(user_id, category_name):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Получаем id категории по ее названию
            category_id_row = await conn.fetchrow(
                'SELECT id FROM categories WHERE name = $1',
                category_name
            )
            if category_id_row:
                category_id = category_id_row['id']
                # Удаляем запись из таблицы Subscriptions
                await conn.execute(
                    'DELETE FROM Subscriptions WHERE user_id = $1 AND category_id = $2',
                    user_id, category_id
                )


async def subscribe_user_to_category(user_id, category_name):
    async with asyncpg.create_pool(dsn=DSN) as pool:
        async with pool.acquire() as conn:
            # Получаем id категории по ее названию
            category_id_row = await conn.fetchrow(
                'SELECT id FROM categories WHERE name = $1',
                category_name
            )
            if category_id_row:
                category_id = category_id_row['id']
                # Добавляем запись в таблицу Subscriptions
                await conn.execute(
                    'INSERT INTO Subscriptions (user_id, category_id) VALUES ($1, $2)',
                    user_id, category_id
                )

# - get_scheduled_posts

# - get_subscribed_posts ДАВАЙ ТИПО ЕЩЕ СПРАШИВАТЬ СКОЛЬКО ПОСЛЕДНИХ ПУБЛИКАЦИЙ ТЕБЕ
# и т.д.

asyncio.run(create_tables())

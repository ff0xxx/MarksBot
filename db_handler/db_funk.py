from aiogram            import Bot
from datetime           import datetime
from config_data.config import load_config


class UserGateway:
    def __init__(self, connect):
        self._connect = connect

    async def create_tables(self):
        await self._connect.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY
            )
        """)

        await self._connect.execute("""
             CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                parent_id BIGINT,
                level BIGINT,
                name TEXT UNIQUE
            )
        """)
        # Добавление категории "news"
        await self._connect.execute("""
                        INSERT INTO categories (level, name) VALUES ($1, $2)
                        ON CONFLICT (name) DO NOTHING
                        """, 1, "news")

        await self._connect.execute("""
            CREATE TABLE IF NOT EXISTS posts (
                id SERIAL PRIMARY KEY,
                content TEXT,
                category_id BIGINT,
                file_id TEXT,
                created_at TIMESTAMP NOT NULL,
                scheduled_at TIMESTAMP NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE ON UPDATE RESTRICT
            )
        """)

        await self._connect.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                category_id BIGINT,
                FOREIGN KEY (user_id) REFERENCES users(user_id),
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE ON UPDATE CASCADE
            )
        """)

    ##### ADD

    async def add_user(self, user_id):
        """Вставляем нового пользователя"""
        # Проверяем, существует ли пользователь
        user_exists = await self._connect.fetchrow("SELECT 1 FROM users WHERE user_id = $1", user_id)

        if not user_exists:
            await self._connect.execute("INSERT INTO users (user_id) VALUES ($1)", user_id)
            # Добавляем подписку на категорию "news"
            await self.add_subscription(user_id, 1)

    async def add_category(self, name):
        """Вставляем новую категорию"""
        await self._connect.execute(
            "INSERT INTO categories (parent_id, level, name) VALUES ($1, $2, $3)",
            None,  # parent_id
            1,     # level
            name
        )

    async def add_subcategory(self, parent_id, name):
        """Вставляем новую подкатегорию"""
        await self._connect.execute(
            "INSERT INTO categories (parent_id, level, name) VALUES ($1, $2, $3)",
            parent_id,
            2,  # level
            name
        )

    async def add_post(self, content, category_id, file_id, scheduled_at):
        """Вставляем новый пост и получаем id вставленной записи"""
        post_id = await self._connect.fetchval(
            """
            INSERT INTO Posts (content, category_id, file_id, created_at, scheduled_at)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
            """,
            content,
            category_id,
            file_id,
            datetime.now(),
            scheduled_at  # type: datetime
        )

        return post_id

    async def add_subscription(self, user_id, category_id):
        """Вставляем новую подписку"""
        await self._connect.execute(
            "INSERT INTO Subscriptions (user_id, category_id) VALUES ($1, $2)",
            user_id,
            category_id
        )

    ##### DELETE

    async def delete_category(self, cat_id: int):
        """Удаляем категорию и связанные с ней подкатегории"""
        await self._connect.execute(
            "DELETE FROM categories WHERE parent_id = $1",
            cat_id
        )

        # Затем удаляем саму категорию
        await self._connect.execute(
            "DELETE FROM categories WHERE id = $1",
            cat_id
        )

    async def delete_post(self, post_id):
        await self._connect.execute(
            "DELETE FROM posts WHERE id = $1",
            post_id
        )


    ##### CATEGORY

    async def get_cat_id_by_name(self, name):
        """Получаем id категории по ее названию"""
        return await self._connect.fetchrow(
            'SELECT id FROM categories WHERE name = $1',
            name
        )

    async def get_all_categories(self, with_subcategories=False):
        if not with_subcategories:
            # Получаем все категории
            return await self._connect.fetch(
                'SELECT id, name FROM categories WHERE level = 1'
            )
        else:
            # Получаем все категории и подкатегории
            return await self._connect.fetch(
                '''
                SELECT id, name 
                FROM categories c1 
                WHERE level = 1 
                AND EXISTS (
                    SELECT 1 
                    FROM categories c2 
                    WHERE c2.parent_id = c1.id
                )
                '''
            )

    async def get_subcats_by_cat_id(self, cat_id):
        """Получаем все подкатегории"""
        return await self._connect.fetch(
            """
            SELECT id, name
            FROM categories 
            WHERE level = 2 
            AND parent_id = $1
            """,
            cat_id
        )

    async def get_all_subcategories_by_user_id(self, user_id):
        """Получаем категории по id пользователя"""
        return await self._connect.fetch(
            """
            SELECT c.id, c.name, c.level
            FROM Subscriptions s
            JOIN categories c ON s.category_id = c.id
            WHERE s.user_id = $1
            AND level = 2
            """,
            user_id
        )

    async def get_subcategories_by_user_id(self, user_id):
        """Получаем подкатегории по id пользователя"""
        return await self._connect.fetch(
            """
            SELECT c.id, c.name
            FROM Subscriptions s
            JOIN categories c ON s.category_id = c.id
            WHERE s.user_id = $1
            AND level = 2
            """,
            user_id
        )

    async def unsubscribe_user_from_category_by_id(self, user_id, cat_id):
        """Удаляем запись из таблицы Subscriptions"""
        await self._connect.execute(
            'DELETE FROM Subscriptions WHERE user_id = $1 AND category_id = $2',
            user_id, cat_id
        )

    async def subscribe_user_to_category_by_id(self, user_id, cat_id):
        """Добавляем запись в таблицу Subscriptions"""
        await self._connect.execute(
            'INSERT INTO Subscriptions (user_id, category_id) VALUES ($1, $2)',
            user_id, cat_id
        )

    ##### ARCHIVE

    async def get_archive_posts(self, user_id, cat_id, count: int):
        """Возвращаем опубликованные посты (для архива)"""
        if user_id in load_config().tg_bot.admin_ids:
            # берем все посты
            posts = await self._connect.fetch(
                """
                SELECT id, content, category_id, file_id
                FROM posts
                WHERE category_id = $1
                ORDER BY created_at DESC 
                LIMIT $2
                """,
                cat_id,
                count
            )
        else:
            # берем только опубликованные посты
            posts = await self._connect.fetch(
                """
                SELECT id, content, category_id, file_id
                FROM posts
                WHERE category_id = $1
                AND NOW() > scheduled_at
                ORDER BY created_at DESC 
                LIMIT $2
                """,
                cat_id,
                count
            )

        return posts

    async def send_archive(self, bot: Bot, posts, user_id):
        """Отправляем пользователю опубликованные посты (как архив)"""
        for post in posts:
            post_id = post['id']
            post_content = post['content']
            post_file = post['file_id']

            if user_id in load_config().tg_bot.admin_ids:
                await bot.send_message(chat_id=user_id, text=f'<b><i>--------id: {post_id}--------</i></b>')
            else:
                await bot.send_message(chat_id=user_id, text=f'<b>------------------</b>')

            if post_file is not None:
                await bot.send_document(chat_id=user_id, document=post_file)
            if post_content is not None:
                await bot.send_message(chat_id=user_id, text=post_content)

    async def is_post_exist(self, post_id):
        """Возвращаем True, если пост существует, и False в противном случае"""
        result = await self._connect.fetchval(
            """
            SELECT EXISTS(
              SELECT 1
              FROM posts
              WHERE id = $1  
            ) AS post_exists;
            """,
            post_id
        )

        return result

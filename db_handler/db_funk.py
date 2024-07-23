from datetime   import datetime
from create_bot import bot


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
                created_at TIMESTAMP NOT NULL,
                scheduled_at TIMESTAMP NOT NULL,
                is_published BOOLEAN DEFAULT FALSE, 
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT ON UPDATE RESTRICT
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

    #### ADD

    async def add_user(self, user_id):
        # Проверяем, существует ли пользователь
        user_exists = await self._connect.fetchrow("SELECT 1 FROM users WHERE user_id = $1", user_id)

        if not user_exists:
            # Вставляем нового пользователя
            await self._connect.execute("INSERT INTO users (user_id) VALUES ($1)", user_id)
            # Добавляем подписку на категорию "news"
            await self.add_subscription(user_id, 1)

    async def add_category(self, name):
        # Вставляем новую категорию
        await self._connect.execute(
            "INSERT INTO categories (parent_id, level, name) VALUES ($1, $2, $3)",
            None,  # parent_id
            1,     # level
            name
        )

    async def add_subcategory(self, parent_id, name):
        # Вставляем новую подкатегорию
        await self._connect.execute(
            "INSERT INTO categories (parent_id, level, name) VALUES ($1, $2, $3)",
            parent_id,
            2,  # level
            name
        )

    async def add_post(self, content, category_id, scheduled_at):
        # Вставляем новый пост
        await self._connect.execute(
            "INSERT INTO Posts (content, category_id, created_at, scheduled_at) VALUES ($1, $2, $3, $4)",
            content,
            category_id,
            datetime.now(),
            scheduled_at  # scheduled_at должен быть типа datetime
        )

    async def add_subscription(self, user_id, category_id):
        # Вставляем новую подписку
        await self._connect.execute(
            "INSERT INTO Subscriptions (user_id, category_id) VALUES ($1, $2)",
            user_id,
            category_id
        )

    #### DELETE

    async def delete_category(self, cat_id: int):
        # Удаляем категорию и связанные с ней подкатегории
        await self._connect.execute(
            "DELETE FROM categories WHERE parent_id = $1",
            cat_id
        )

        # Затем удаляем саму категорию
        await self._connect.execute(
            "DELETE FROM categories WHERE id = $1",
            cat_id
        )

    async def delete_post(self, post: int):
        """сначала напиши высылание архива и уже похоже на это будет тут"""
        pass


    ##### CATEGORY

    async def get_cat_id_by_name(self, name):
        # Получаем id категории по ее названию
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
        # Получаем все подкатегории
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
        # Получаем категории по id пользователя
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
        # Получаем подкатегории по id пользователя
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
        # Удаляем запись из таблицы Subscriptions
        await self._connect.execute(
            'DELETE FROM Subscriptions WHERE user_id = $1 AND category_id = $2',
            user_id, cat_id
        )

    async def subscribe_user_to_category_by_id(self, user_id, cat_id):
        # Добавляем запись в таблицу Subscriptions
        await self._connect.execute(
            'INSERT INTO Subscriptions (user_id, category_id) VALUES ($1, $2)',
            user_id, cat_id
        )

    ##### POSTS

    async def get_subscribers_for_post(self, post_id):
        """Возвращает список user_ids которые должны получить данный пост"""
        user_ids = await self._connect.fetch(
            """
            SELECT u.user_id
            FROM subscriptions s
            JOIN users u ON s.user_id = u.user_id
            WHERE s.category_id = (
              SELECT category_id 
              FROM posts
              WHERE id = $1
            );
            """,
            post_id
        )

        return user_ids

    async def check_scheduled_posts(self):
        """Возвращает посты, scheduled_at которых наступило"""
        scheduled_posts = await self._connect.fetch(
            """
            SELECT id, content, category_id, scheduled_at
            FROM posts
            WHERE scheduled_at <= NOW() AND is_published = FALSE;
            """
        )

        return scheduled_posts

    async def send_post_to_subscribers(self, scheduled_posts):
        """Отправляет посты, scheduled_at которых наступило, всем кому нужно"""
        for post in scheduled_posts:
            post_id = post['id']
            post_content = post['content']
            category_id = post['category_id']

            user_ids = await self.get_subscribers_for_post(post_id)

            # Отправляем сообщение каждому подписчику
            for user in user_ids:
                await bot.send_message(chat_id=user['user_id'], text=post_content)

            # Обновляем статус поста на выложенный
            await self._connect.execute(
                """
                UPDATE posts
                SET is_published = TRUE
                WHERE id = $1;
                """,
                post_id
            )

    # - Удалить пост

    async def get_archive_posts(self, cat_id, count: int):
        # ИЗМЕНИ ТУТ FALSE НА TRUE !!!!!!!!!!!!!!!!!
        # @!!!!!!!!!!!!@!!!!!!!!!!!!!!!
        # @@@@@@@@@@@@@@@@@@@@@@@@@!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        posts = await self._connect.fetch(
            """
            SELECT id, content, category_id
            FROM posts
            WHERE category_id = $1
            AND is_published = FALSE
            ORDER BY created_at DESC 
            LIMIT $2
            """,
            cat_id,
            count
        )
        return posts

    async def send_archive(self, posts, user_id):
        for post in posts:
            post_content = post['content']
            await bot.send_message(chat_id=user_id, text=post_content)

import sqlite3


# отдельный класс, отвечающий за взаимодействие с базой данных
class DatabaseManager:
    def __init__(self, database_file):  # 'tg.db'
        self.database_file = database_file
        self.connection = sqlite3.connect(database_file)  # чтобы создать бд, если ее нет
        self.cursor = self.connection.cursor()

    def create_tables(self):
        # нет поля с категориями, потому что есть
        # отдельная таблица Subscriptions для этого
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY
            )
        """)

        # ахахаххахахаха level разрази меня гром
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Categories (
                id INTEGER PRIMARY KEY,
                parent_id INTEGER,
                level INTEGER,
                name TEXT UNIQUE
            )
        """)
        # Добавление категории "news"
        self.cursor.execute(
            "INSERT OR IGNORE INTO Categories (level, name) VALUES (?, ?)",
            (1, "news")
        )

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Posts (
                id INTEGER PRIMARY KEY,
                content TEXT,
                category_id INTEGER,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                scheduled_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES Categories(id) ON DELETE RESTRICT ON UPDATE RESTRICT,
                CHECK (scheduled_at >= created_at)
            )
        """)
        # self.cursor.execute("CREATE INDEX ON Posts (category_id)")
        # self.cursor.execute("CREATE INDEX ON Posts (scheduled_at)")

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Subscriptions (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                category_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES Users(user_id),
                FOREIGN KEY (category_id) REFERENCES Categories(id)
            )
        """)

        self.connection.commit()

    def add_user(self, user_id):
        self.cursor.execute("SELECT 1 FROM Users WHERE user_id = ?", (user_id,))
        user_exists = self.cursor.fetchone()

        if not user_exists:
            self.cursor.execute(
                "INSERT INTO Users (user_id) VALUES (?)",
                (user_id,)
            )
            self.connection.commit()
            # Добавляем подписку на категорию "news"
            self.add_subscription(user_id, 1)

    def add_category(self, parent_id, level, name):  # subcategory: меняй level (с 1 на 2)
        self.cursor.execute(
            "INSERT INTO Categories (parent_id, level, name) VALUES (?, ?, ?)",
            (parent_id, level, name)
        )
        self.connection.commit()

    def add_post(self, content, category_id, scheduled_at):
        self.cursor.execute(
            "INSERT INTO Posts (content, category_id, scheduled_at) VALUES (?, ?, ?)",
            (content, category_id, scheduled_at)  # scheduled_at = datetime.datetime(2023, 6, 1, 12, 0, 0)
        )
        self.connection.commit()

    def add_subscription(self, user_id, category_id):
        self.cursor.execute(
            'INSERT INTO Subscriptions (user_id, category_id) VALUES (?, ?)',
            (user_id, category_id)
        )
        self.connection.commit()

    # - get_user_by_id
    # - get_category_by_id
    # - get_subscribed_posts
    # - get_scheduled_posts
    # и т.д.

    def close(self):
        self.connection.close()


db = DatabaseManager('tg.db')

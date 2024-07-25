import asyncpg
from config_data.config import load_config


async def send_post_to_subscribers(bot, post_content, post_id):
    """Отправляет запланированные посты нужным подписчикам"""
    # отдельный пулл создается чтоб узнавать нынешних подписчиков
    async with asyncpg.create_pool(dsn=load_config().tg_bot.dsn) as pool:
        async with pool.acquire() as connection:
            user_ids = await connection.fetch(
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

        for user in user_ids:
            await bot.send_message(chat_id=user['user_id'], text=post_content)

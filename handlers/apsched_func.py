import asyncpg
from aiogram            import Bot
from config_data.config import load_config
from aiogram.types import ChatMember


async def send_post_to_subscribers(bot: Bot, post_id, user_id, post_content, file_id):
    """Отправляет запланированные посты нужным подписчикам"""
    # отдельный пулл создается чтоб узнавать нынешних подписчиков
    async with asyncpg.create_pool(dsn=load_config().tg_bot.dsn) as pool:
        async with pool.acquire() as connection:
            try:
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
                    try:
                        if file_id is not None:
                            await bot.send_document(chat_id=user['user_id'], document=file_id)
                        if post_content is not None:
                            await bot.send_message(chat_id=user['user_id'], text=post_content)
                    except:
                        continue

            except Exception as e:
                print(e)
                await bot.send_message(chat_id=user_id, text='Не удалось отправить пост')

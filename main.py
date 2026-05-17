import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties

from config import BOT_TOKEN, ALLOWED_USERS
from bot.filters.auth import AuthorizedUser, AuthorizedCallback
from bot.handlers import start, chat, settings, usage

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

dp.message.filter(AuthorizedUser(ALLOWED_USERS))
dp.callback_query.filter(AuthorizedCallback(ALLOWED_USERS))

dp.include_routers(
    start.router,
    chat.router,
    settings.router,
    usage.router,
)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

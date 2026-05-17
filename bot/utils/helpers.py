import asyncio
from aiogram import Bot
from aiogram.enums import ChatAction


async def _typing_loop(bot: Bot, chat_id: int, stop: asyncio.Event):
    while not stop.is_set():
        try:
            await bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)
            await asyncio.sleep(3.5)
        except Exception:
            break


async def with_typing(bot: Bot, chat_id: int, coro):
    stop = asyncio.Event()
    task = asyncio.create_task(_typing_loop(bot, chat_id, stop))
    try:
        return await coro
    finally:
        stop.set()
        await asyncio.sleep(0)

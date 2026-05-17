from aiogram.filters import Filter
from aiogram.types import Message
from bot.services.memory import get_mode


class ModeFilter(Filter):
    def __init__(self, mode: str):
        self.mode = mode

    async def __call__(self, message: Message) -> bool:
        return get_mode(message.from_user.id) == self.mode

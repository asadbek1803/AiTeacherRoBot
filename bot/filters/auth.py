from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery


class AuthorizedUser(Filter):
    def __init__(self, allowed_users: list[int]):
        self.allowed_users = allowed_users

    async def __call__(self, message: Message) -> bool:
        if message.from_user.id in self.allowed_users:
            return True
        await message.answer("⛔ Sizda ushbu botdan foydalanish uchun ruxsat yo'q.")
        return False


class AuthorizedCallback(Filter):
    def __init__(self, allowed_users: list[int]):
        self.allowed_users = allowed_users

    async def __call__(self, callback: CallbackQuery) -> bool:
        if callback.from_user.id in self.allowed_users:
            return True
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return False

from aiogram import Router, F
from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from config import ALLOWED_USERS
from bot.services.memory import is_user_allowed, add_pending_request
from bot.keyboards.menus import request_access_menu

router = Router()


class AuthorizedUser(Filter):
    def __init__(self, allowed_users: list[int]):
        self.allowed_users = allowed_users

    async def __call__(self, message: Message) -> bool:
        uid = message.from_user.id
        if uid in self.allowed_users:
            return True
        return is_user_allowed(uid)


class AuthorizedCallback(Filter):
    def __init__(self, allowed_users: list[int]):
        self.allowed_users = allowed_users

    async def __call__(self, callback: CallbackQuery) -> bool:
        uid = callback.from_user.id
        if uid in self.allowed_users:
            return True
        return is_user_allowed(uid)


class NotAuthorized(Filter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        uid = event.from_user.id
        if uid in ALLOWED_USERS:
            return False
        return not is_user_allowed(uid)


@router.message(NotAuthorized())
async def unauthorized_message(message: Message):
    await message.answer(
        "⛔ Botdan foydalanish uchun ruxsat yo'q.\n\n"
        "Adminstratorga so'rov yuborish uchun quyidagi tugmani bosing:",
        reply_markup=request_access_menu(),
    )


@router.callback_query(NotAuthorized(), F.data == "request_access")
async def request_access_handler(callback: CallbackQuery):
    uid = callback.from_user.id
    add_pending_request(uid, callback.from_user.username, callback.from_user.full_name)
    await callback.message.edit_text(
        "✅ So'rovingiz adminstratorga yuborildi. Iltimos, javobni kuting."
    )

    from bot.handlers.admin import notify_admins

    await notify_admins(
        callback.bot,
        uid,
        callback.from_user.full_name,
        callback.from_user.username,
    )
    await callback.answer()

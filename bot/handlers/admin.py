from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest
from config import ADMIN_IDS
from bot.services.memory import get_pending_requests, approve_user, reject_user
from bot.keyboards.menus import admin_menu, admin_request_keyboard

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


async def show_admin_panel(target: Message | CallbackQuery):
    requests = get_pending_requests()
    if not requests:
        text = "👮‍♂️ <b>Admin panel</b>\n\nHech qanday kutilgan so'rovlar yo'q."
    else:
        text = f"👮‍♂️ <b>Admin panel</b>\n\nKutilgan so'rovlar: {len(requests)}\n"
        for req in requests:
            name = req["full_name"]
            username = f"@{req['username']}" if req["username"] else "no username"
            text += f"\n🆔 <code>{req['user_id']}</code> — {name} ({username})"
    if isinstance(target, Message):
        await target.answer(text, reply_markup=admin_menu(len(requests)))
    else:
        try:
            await target.message.edit_text(text, reply_markup=admin_menu(len(requests)))
        except TelegramBadRequest as e:
            if "message is not modified" not in str(e):
                raise


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        await message.answer("⛔ Bu buyruq faqat adminlar uchun.")
        return
    await show_admin_panel(message)


@router.callback_query(F.data == "admin_refresh")
async def admin_refresh(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await show_admin_panel(callback)
    await callback.answer()


@router.callback_query(F.data == "admin_show_requests")
async def admin_show_requests(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    requests = get_pending_requests()
    if not requests:
        await callback.message.edit_text("Hech qanday kutilgan so'rovlar yo'q.")
        await callback.answer()
        return
    req = requests[0]
    text = (
        f"👤 <b>Foydalanuvchi:</b> {req['full_name']}\n"
        f"🆔 ID: <code>{req['user_id']}</code>\n"
        f"📛 Username: @{req['username'] or 'yoq'}\n"
        f"📅 Sana: {req['created_at']}\n\n"
        f"So'rovlarning umumiy soni: {len(requests)}"
    )
    try:
        await callback.message.edit_text(text, reply_markup=admin_request_keyboard(req['user_id']))
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("admin_approve_"))
async def admin_approve(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    user_id = int(callback.data.replace("admin_approve_", ""))
    approve_user(user_id)
    try:
        await callback.message.edit_text(f"✅ Foydalanuvchi <code>{user_id}</code> tasdiqlandi.")
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    try:
        await callback.bot.send_message(
            user_id,
            "✅ <b>Tasdiqlandi!</b>\n\nAdmin sizni tasdiqladi. Endi botdan to'liq foydalanishingiz mumkin.\n\n/start - boshlash",
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data.startswith("admin_reject_"))
async def admin_reject(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    user_id = int(callback.data.replace("admin_reject_", ""))
    reject_user(user_id)
    try:
        await callback.message.edit_text(f"❌ Foydalanuvchi <code>{user_id}</code> rad etildi.")
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    try:
        await callback.bot.send_message(
            user_id,
            "❌ <b>Rad etildi</b>\n\nAfsuski, botdan foydalanish so'rovingiz rad etildi.",
        )
    except Exception:
        pass
    await callback.answer()


@router.callback_query(F.data == "admin_back")
async def admin_back(callback: CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("⛔ Ruxsat yo'q", show_alert=True)
        return
    await show_admin_panel(callback)
    await callback.answer()


async def notify_admins(bot, user_id: int, full_name: str, username: str | None):
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    text = (
        f"📩 <b>Yangi so'rov!</b>\n\n"
        f"👤 {full_name}\n"
        f"🆔 <code>{user_id}</code>\n"
        f"📛 @{username or 'yoq'}"
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Tasdiqlash", callback_data=f"admin_approve_{user_id}"
                ),
                InlineKeyboardButton(
                    text="❌ Rad etish", callback_data=f"admin_reject_{user_id}"
                ),
            ],
        ]
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text, reply_markup=kb)
        except Exception:
            pass

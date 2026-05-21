from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from bot.filters.auth import AuthorizedUser, AuthorizedCallback
from config import ALLOWED_USERS
from bot.keyboards.menus import main_menu

router = Router()

WELCOME_TEXT = (
    "🇰🇷 <b>AiTeacher</b> — Koreys tili o'qituvchingiz!\n\n"
    "👋 Salom! Istalgan narsani so'rang:\n"
    "• ✍️ Matn yozing — so'z, gap, grammatika, TOPIK\n"
    "• 🎤 Ovozli xabar yuboring — nutq amaliyoti\n"
    "• ⚙️ Settings — daraja va modelni sozlash\n"
    "• 📊 Usage — limitlar va holat\n\n"
    "Hammasini bitta chatda so'rang!"
)


@router.message(Command("start", "menu"), AuthorizedUser(ALLOWED_USERS))
async def cmd_start(message: Message):
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())


@router.callback_query(F.data == "back_menu", AuthorizedCallback(ALLOWED_USERS))
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(WELCOME_TEXT, reply_markup=main_menu())
    await callback.answer()

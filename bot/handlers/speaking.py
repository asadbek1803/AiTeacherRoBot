from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.filters.auth import AuthorizedUser, AuthorizedCallback
from bot.filters.mode import ModeFilter
from config import ALLOWED_USERS
from bot.services.groq_client import ask_ai
from bot.services.memory import (
    set_mode,
    get_level,
    get_dialog,
    set_dialog,
    clear_dialog,
)
from bot.keyboards.menus import main_menu, speaking_actions

router = Router()

SPEAKING_PROMPT = (
    "You are a Korean conversation partner. "
    "Speak primarily in Korean at the user's level. "
    "Keep responses short (2-3 sentences). "
    "If user makes a mistake, briefly correct it once then continue naturally. "
    "Ask natural follow-up questions. "
    "The user wants to practice speaking."
)


@router.callback_query(F.data == "mode_speaking", AuthorizedCallback(ALLOWED_USERS))
async def speaking_start(callback: CallbackQuery):
    clear_dialog(callback.from_user.id)
    set_mode(callback.from_user.id, "speaking")
    level = get_level(callback.from_user.id)
    response = await ask_ai(
        SPEAKING_PROMPT,
        "Start a conversation with me in Korean. Ask me a simple question to begin.",
        level,
    )
    set_dialog(callback.from_user.id, [{"role": "assistant", "content": response}])
    await callback.message.edit_text(response, reply_markup=speaking_actions())
    await callback.answer()


@router.message(ModeFilter("speaking"), F.text, AuthorizedUser(ALLOWED_USERS))
async def speaking_handler(message: Message):
    level = get_level(message.from_user.id)
    dialog = get_dialog(message.from_user.id)

    response = await ask_ai(SPEAKING_PROMPT, message.text, level, dialog)

    new_msgs = dialog + [
        {"role": "user", "content": message.text},
        {"role": "assistant", "content": response},
    ]
    if len(new_msgs) > 20:
        new_msgs = new_msgs[-20:]
    set_dialog(message.from_user.id, new_msgs)

    await message.answer(response, reply_markup=speaking_actions())


@router.callback_query(F.data == "speaking_stop", AuthorizedCallback(ALLOWED_USERS))
async def speaking_stop(callback: CallbackQuery):
    clear_dialog(callback.from_user.id)
    set_mode(callback.from_user.id, "chat")
    await callback.message.edit_text(
        "✅ Speaking practice ended.\n\n"
        "Qaytadan boshlash uchun 🎤 Speaking tugmasini bosing.",
        reply_markup=main_menu(),
    )
    await callback.answer()

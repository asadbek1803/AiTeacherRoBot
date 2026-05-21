import os
from io import BytesIO
from aiogram import Router, F, Bot
from aiogram.types import Message
from bot.filters.auth import AuthorizedUser
from config import ALLOWED_USERS
from bot.services.ai_router import ask_ai
from bot.services.whisper_client import transcribe_audio
from bot.services.memory import get_level
from bot.keyboards.menus import main_menu
from bot.utils.helpers import with_typing

router = Router()

prompt_path = os.path.join(os.path.dirname(__file__), "..", "..", "system_prompt.txt")
with open(prompt_path, "r", encoding="utf-8") as f:
    CHAT_SYSTEM_PROMPT = f.read()


@router.message(F.text, AuthorizedUser(ALLOWED_USERS))
async def chat_handler(message: Message, bot: Bot):
    uid = message.from_user.id
    level = get_level(uid)
    response = await with_typing(
        bot,
        message.chat.id,
        ask_ai(CHAT_SYSTEM_PROMPT, message.text, level, user_id=uid),
    )
    await message.answer(response, reply_markup=main_menu())


@router.message(F.voice, AuthorizedUser(ALLOWED_USERS))
async def voice_handler(message: Message, bot: Bot):
    uid = message.from_user.id
    file = await bot.get_file(message.voice.file_id)
    buf = BytesIO()
    await bot.download(file=file, destination=buf)
    audio_bytes = buf.getvalue()

    try:
        text = await transcribe_audio(audio_bytes)
    except Exception as e:
        await message.answer(f"⚠️ {str(e)}")
        return

    if not text:
        await message.answer(
            "⚠️ Ovozni tushuna olmadim. Iltimos, qaytadan yozib yuboring yoki sekinroq gapiring."
        )
        return

    level = get_level(uid)
    response = await with_typing(
        bot,
        message.chat.id,
        ask_ai(CHAT_SYSTEM_PROMPT, text, level, user_id=uid),
    )
    await message.answer(response, reply_markup=main_menu())

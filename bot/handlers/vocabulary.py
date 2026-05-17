from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.filters.mode import ModeFilter
from bot.services.groq_client import ask_ai
from bot.services.memory import set_mode, get_level
from bot.keyboards.menus import main_menu

router = Router()

VOCAB_PROMPT = (
    "You are a Korean vocabulary teacher. "
    "When given a Korean word, provide:\n"
    "🇰🇷 Word: \n🇺🇿 Meaning: \n🔊 Pronunciation: \n✨ Examples:\n1. \n2. \n"
    "Keep it concise. Explain in Uzbek."
)


@router.callback_query(F.data == "mode_vocab")
async def vocab_mode_set(callback: CallbackQuery):
    set_mode(callback.from_user.id, "vocabulary")
    await callback.message.edit_text(
        "📚 <b>Vocabulary</b>\n\n"
        "Koreyscha so'z yozing — men tarjima qilaman va misollar ko'rsataman.\n\n"
        "Misol: <code>사랑</code>  <code>감사합니다</code>",
        reply_markup=main_menu(),
    )
    await callback.answer()


@router.message(ModeFilter("vocabulary"), F.text)
async def vocab_handler(message: Message):
    level = get_level(message.from_user.id)
    response = await ask_ai(VOCAB_PROMPT, message.text, level)
    await message.answer(response, reply_markup=main_menu())

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.filters.auth import AuthorizedUser, AuthorizedCallback
from bot.filters.mode import ModeFilter
from config import ALLOWED_USERS
from bot.services.groq_client import ask_ai
from bot.services.memory import set_mode, get_level
from bot.keyboards.menus import main_menu

router = Router()

GRAMMAR_PROMPT = (
    "You are a Korean grammar teacher. Explain grammar points simply.\n"
    "Structure:\n"
    "- Meaning in Uzbek\n"
    "- Structure (how to use)\n"
    "- Usage notes\n"
    "- 2 examples\n"
    "- Common mistake\n"
    "Keep it short and practical. Answer in Uzbek."
)


@router.callback_query(F.data == "mode_grammar", AuthorizedCallback(ALLOWED_USERS))
async def grammar_mode_set(callback: CallbackQuery):
    set_mode(callback.from_user.id, "grammar")
    await callback.message.edit_text(
        "📝 <b>Grammar</b>\n\n"
        "Grammatikani tushuntirib beraman. Qoida nomini yoki misol yozing.\n\n"
        "Misol: <code>은/는</code>  <code>-(으)세요</code>",
        reply_markup=main_menu(),
    )
    await callback.answer()


@router.message(ModeFilter("grammar"), F.text, AuthorizedUser(ALLOWED_USERS))
async def grammar_handler(message: Message):
    level = get_level(message.from_user.id)
    response = await ask_ai(GRAMMAR_PROMPT, message.text, level)
    await message.answer(response, reply_markup=main_menu())

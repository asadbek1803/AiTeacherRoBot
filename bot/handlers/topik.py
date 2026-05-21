from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.filters.auth import AuthorizedUser, AuthorizedCallback
from bot.filters.mode import ModeFilter
from config import ALLOWED_USERS
from bot.services.groq_client import ask_ai
from bot.services.memory import get_level, update_user, get_user, set_mode
from bot.keyboards.menus import main_menu, topik_menu

router = Router()

TOPIK_GEN_PROMPT = {
    "vocab": (
        "Generate a TOPIK vocabulary question. "
        "Include a Korean word and 4 multiple choice meanings in Uzbek. "
        "Mark the correct answer with *. Return as: Question, choices, answer key."
    ),
    "grammar": (
        "Generate a TOPIK grammar question. "
        "Include a Korean sentence with a blank and 4 grammar choices. "
        "Mark the correct answer with *. Return as: Question, choices, answer key."
    ),
    "reading": (
        "Generate a short TOPIK reading passage (3-4 sentences) in Korean "
        "with 2 comprehension questions in Uzbek. Include answer key."
    ),
    "writing": (
        "Generate a TOPIK writing topic. "
        "Give a topic in Korean and ask the user to write 3-5 sentences. "
        "Return only the topic prompt."
    ),
    "speaking": (
        "Generate a TOPIK speaking topic. "
        "Give a question in Korean that the user should answer orally. "
        "Return only the question."
    ),
}

TOPIK_CHECK_PROMPT = (
    "You are a TOPIK exam grader. Check the user's answer and:\n"
    "1. Mark correctness (✅/❌)\n"
    "2. Give score out of 100\n"
    "3. Explain mistakes briefly in Uzbek\n"
    "4. Provide correct answer\n"
    "Keep it concise."
)


@router.callback_query(F.data == "mode_topik", AuthorizedCallback(ALLOWED_USERS))
async def topik_menu_show(callback: CallbackQuery):
    set_mode(callback.from_user.id, "topik")
    await callback.message.edit_text(
        "🇰🇷 <b>TOPIK Practice</b>\n\nMashq turini tanlang:",
        reply_markup=topik_menu(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("topik_"), AuthorizedCallback(ALLOWED_USERS))
async def topik_generate(callback: CallbackQuery):
    topic = callback.data.replace("topik_", "")
    level = get_level(callback.from_user.id)

    prompt = TOPIK_GEN_PROMPT.get(topic, TOPIK_GEN_PROMPT["vocab"])
    response = await ask_ai(
        "You are a TOPIK test maker. Generate realistic TOPIK practice questions.",
        prompt,
        level,
    )

    update_user(
        callback.from_user.id, topik_topic=topic, topik_question=response
    )
    await callback.message.edit_text(response, reply_markup=main_menu())
    await callback.answer()


@router.message(ModeFilter("topik"), F.text, AuthorizedUser(ALLOWED_USERS))
async def topik_answer(message: Message):
    level = get_level(message.from_user.id)
    user_data = get_user(message.from_user.id)
    question = user_data.get("topik_question", "")
    topic = user_data.get("topik_topic", "vocab")

    response = await ask_ai(
        TOPIK_CHECK_PROMPT,
        f"Question ({topic}): {question}\n\nUser answer: {message.text}",
        level,
    )

    await message.answer(response, reply_markup=main_menu())
    update_user(message.from_user.id, topik_question=None, topik_topic=None)

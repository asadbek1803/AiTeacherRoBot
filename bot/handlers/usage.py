from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from bot.filters.auth import AuthorizedCallback
from config import ALLOWED_USERS
from bot.services.memory import get_model
from bot.services.groq_client import get_remaining_requests as groq_req
from bot.services.groq_client import get_remaining_tokens as groq_tok
from bot.services.gemini_client import get_remaining_requests as gemini_req
from bot.services.whisper_client import get_whisper_remaining
from config import GEMINI_LIMITS, CHAT_LIMITS, WHISPER_LIMITS, WHISPER_MODEL, AVAILABLE_MODELS
from bot.keyboards.menus import main_menu

router = Router()


def _status(val, green, yellow):
    if val is None:
        return "⚪"
    return "🟢" if val > green else ("🟡" if val > yellow else "🔴")


def _build_chat_section(model, limits):
    if model == "gemini":
        req = gemini_req()
        name = "Gemini 2.0 Flash"
        return (
            f"━━━ <b>{name}</b> ━━━\n"
            f"{_status(req, 8, 3)} Requests left: <b>{req if req is not None else 'N/A'}</b> / {limits['rpm']}/min\n"
            f"📌 Daily: {limits['rpd']} req\n"
        )
    req = groq_req()
    tok = groq_tok()
    return (
        f"━━━ <b>Groq (Qwen 3 32B)</b> ━━━\n"
        f"{_status(req, 30, 10)} Requests left: <b>{req if req is not None else 'N/A'}</b> / {limits['rpm']}/min\n"
        f"{_status(tok, 3000, 1000)} Tokens left: <b>{tok if tok is not None else 'N/A'}</b> / {limits['tpm']}/min\n"
        f"📌 Daily: {limits['rpd']} req / {limits['tpd']} tok\n"
    )


@router.callback_query(F.data == "mode_usage", AuthorizedCallback(ALLOWED_USERS))
async def usage_show(callback: CallbackQuery):
    uid = callback.from_user.id
    active_model = get_model(uid)
    active_name = AVAILABLE_MODELS.get(active_model, active_model)

    whis = get_whisper_remaining()
    chat_section = _build_chat_section(active_model, CHAT_LIMITS if active_model == "groq" else GEMINI_LIMITS)

    text = (
        "📊 <b>AiTeacher Status</b>\n\n"
        f"🔵 Active model: <b>{active_name}</b>\n\n"
        f"{chat_section}\n"
        "━━━ <b>Voice (Whisper)</b> ━━━\n"
        f"{_status(whis, 10, 5)} Transcriptions left: <b>{whis if whis is not None else 'N/A'}</b> / {WHISPER_LIMITS['rpm']}/min\n"
        f"📌 Daily: {WHISPER_LIMITS['rpd']} req / {WHISPER_LIMITS['aps_day']} sec"
    )

    try:
        await callback.message.edit_text(text, reply_markup=main_menu())
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()

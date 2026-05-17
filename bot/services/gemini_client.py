import asyncio
import warnings
from datetime import datetime, timedelta

with warnings.catch_warnings():
    warnings.simplefilter("ignore", FutureWarning)
    import google.generativeai as genai
from config import GEMINI_API_KEY, GEMINI_MODEL
from bot.services.groq_client import clean_response

genai.configure(api_key=GEMINI_API_KEY)

_calls = []
WINDOW = 60


def _count_recent():
    now = datetime.now()
    cutoff = now - timedelta(seconds=WINDOW)
    return sum(1 for t in _calls if t > cutoff)


def _track_call():
    _calls.append(datetime.now())
    cutoff = datetime.now() - timedelta(seconds=WINDOW)
    while _calls and _calls[0] < cutoff:
        _calls.pop(0)


def get_remaining_requests():
    used = _count_recent()
    return max(0, 15 - used)


async def ask_ai(
    system_prompt: str,
    user_message: str,
    level: str = "beginner",
    messages: list = None,
) -> str:
    try:
        model = genai.GenerativeModel(
            GEMINI_MODEL, system_instruction=system_prompt
        )
        prompt = f"[Level: {level}] {user_message}"

        def _sync():
            _track_call()
            if messages:
                chat = model.start_chat()
                for msg in messages:
                    role = "user" if msg["role"] == "user" else "model"
                    chat.history.append({"role": role, "parts": [msg["content"]]})
                return chat.send_message(prompt)
            return model.generate_content(prompt)

        response = await asyncio.to_thread(_sync)
        return clean_response(response.text)

    except Exception as e:
        err = str(e)
        if "429" in err or "RESOURCE_EXHAUSTED" in err:
            raise QuotaExceededError(err)
        return f"⚠️ Xatolik (Gemini): {err}"


class QuotaExceededError(Exception):
    pass

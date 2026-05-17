from bot.services.memory import get_user, set_model
from bot.services.groq_client import ask_ai as groq_ask
from bot.services.gemini_client import ask_ai as gemini_ask
from bot.services.gemini_client import QuotaExceededError


async def ask_ai(
    system_prompt: str,
    user_message: str,
    level: str = "beginner",
    user_id: int = None,
    messages: list = None,
) -> str:
    model = "groq"
    if user_id:
        model = get_user(user_id).get("model", "groq")

    if model == "gemini":
        try:
            return await gemini_ask(system_prompt, user_message, level, messages)
        except QuotaExceededError:
            if user_id:
                set_model(user_id, "groq")
            return (
                "⚠️ Gemini kvotasi tugagan. Avtomatik ravishda <b>Groq</b> modeliga o'tildi.\n\n"
                "🔧 Google Cloud Console → API & Services → "
                "Generative Language API tekshiring yoki billing ulang.\n\n"
                "---\n" + await groq_ask(system_prompt, user_message, level, messages)
            )

    return await groq_ask(system_prompt, user_message, level, messages)

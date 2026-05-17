import asyncio
import re
from openai import OpenAI
from config import GROQ_API_KEY, GROQ_BASE_URL, CHAT_MODEL

client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

_remaining_requests = None
_remaining_tokens = None

ALLOWED_HTML = frozenset({'b', 'i', 'u', 's', 'a', 'code', 'pre', 'span', 'br'})


def get_remaining_requests():
    return _remaining_requests


def get_remaining_tokens():
    return _remaining_tokens


def _update_limits(headers: dict):
    global _remaining_requests, _remaining_tokens
    try:
        if "x-ratelimit-remaining-requests" in headers:
            _remaining_requests = int(headers["x-ratelimit-remaining-requests"])
        if "x-ratelimit-remaining-tokens" in headers:
            _remaining_tokens = int(headers["x-ratelimit-remaining-tokens"])
    except Exception:
        pass


def clean_response(text: str) -> str:
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    text = re.sub(r'<thought>.*?</thought>', '', text, flags=re.DOTALL)
    def _html_filter(m):
        tag = re.match(r'</?(\w+)', m.group(0))
        return m.group(0) if tag and tag.group(1).lower() in ALLOWED_HTML else ''
    text = re.sub(r'<[^>]*>', _html_filter, text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


async def ask_ai(
    system_prompt: str,
    user_message: str,
    level: str = "beginner",
    messages: list = None,
) -> str:
    try:
        msg_list = [{"role": "system", "content": system_prompt}]
        if messages:
            msg_list.extend(messages)
        msg_list.append(
            {"role": "user", "content": f"[Level: {level}] {user_message}"}
        )

        def _sync():
            raw = client.chat.completions.with_raw_response.create(
                model=CHAT_MODEL,
                messages=msg_list,
                temperature=0.3,
            )
            return raw.headers, raw.parse()

        headers, response = await asyncio.to_thread(_sync)
        _update_limits(dict(headers))
        return clean_response(response.choices[0].message.content)

    except Exception as e:
        return f"⚠️ Xatolik: {str(e)}"
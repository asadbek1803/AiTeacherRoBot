import asyncio
import io
from openai import OpenAI
from config import GROQ_API_KEY, GROQ_BASE_URL, WHISPER_MODEL

client = OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)

_whisper_remaining = None


def get_whisper_remaining():
    return _whisper_remaining


async def transcribe_audio(audio_bytes: bytes) -> str:
    global _whisper_remaining
    try:
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "voice.ogg"

        def _sync():
            raw = client.audio.transcriptions.with_raw_response.create(
                model=WHISPER_MODEL, file=audio_file
            )
            return raw.headers, raw.parse()

        headers, transcription = await asyncio.to_thread(_sync)
        try:
            if "x-ratelimit-remaining-requests" in dict(headers):
                _whisper_remaining = int(headers["x-ratelimit-remaining-requests"])
        except Exception:
            pass

        return transcription.text.strip()

    except Exception as e:
        raise Exception(f"Ovozni tushunishda xatolik: {str(e)}")

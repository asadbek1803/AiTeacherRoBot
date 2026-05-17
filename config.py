import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x]
ALLOWED_USERS = [int(x) for x in os.getenv("ALLOWED_USERS", "").split(",") if x]
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

CHAT_MODEL = "qwen/qwen3-32b"
GEMINI_MODEL = "gemini-3.1-flash-lite"
WHISPER_MODEL = "whisper-large-v3-turbo"

CHAT_LIMITS = {"rpm": 60, "rpd": 1000, "tpm": 6000, "tpd": 500000}
GEMINI_LIMITS = {"rpm": 15, "rpd": 1500}
WHISPER_LIMITS = {"rpm": 20, "rpd": 2000, "aps_hour": 7200, "aps_day": 28800}

AVAILABLE_MODELS = {
    "groq": "🤖 Groq (Qwen 3 32B)",
    "gemini": "🧠 Gemini 2.0 Flash",
}

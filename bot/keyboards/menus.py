from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="⚙️ Settings", callback_data="mode_settings"),
                InlineKeyboardButton(text="📊 Usage", callback_data="mode_usage"),
            ],
        ]
    )


def settings_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Level", callback_data="settings_level"),
                InlineKeyboardButton(text="🧠 Model", callback_data="settings_model"),
            ],
            [InlineKeyboardButton(text="🔙 Back", callback_data="back_menu")],
        ]
    )


def level_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔰 Beginner", callback_data="level_beginner")],
            [InlineKeyboardButton(text="🌱 Intermediate", callback_data="level_intermediate")],
            [InlineKeyboardButton(text="🔥 Advanced", callback_data="level_advanced")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_main")],
        ]
    )


def model_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤖 Groq (Qwen 3 32B)", callback_data="model_groq")],
            [InlineKeyboardButton(text="🧠 Gemini 2.0 Flash", callback_data="model_gemini")],
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="settings_main")],
        ]
    )

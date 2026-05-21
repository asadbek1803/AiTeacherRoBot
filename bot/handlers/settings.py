from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from bot.filters.auth import AuthorizedCallback
from config import ALLOWED_USERS, AVAILABLE_MODELS
from bot.services.memory import set_level, set_model, get_level, get_model
from bot.keyboards.menus import main_menu, settings_menu, level_menu, model_menu

router = Router()

LEVEL_NAMES = {
    "beginner": "🔰 Beginner",
    "intermediate": "🌱 Intermediate",
    "advanced": "🔥 Advanced",
}


@router.callback_query(F.data == "mode_settings", AuthorizedCallback(ALLOWED_USERS))
async def settings_show(callback: CallbackQuery):
    uid = callback.from_user.id
    level_icon = LEVEL_NAMES.get(get_level(uid), get_level(uid))
    model_icon = AVAILABLE_MODELS.get(get_model(uid), get_model(uid))
    text = (
        f"⚙️ <b>Settings</b>\n\n"
        f"📊 Level: <b>{level_icon}</b>\n"
        f"🧠 Model: <b>{model_icon}</b>\n\n"
        f"Bo'limni tanlang:"
    )
    try:
        await callback.message.edit_text(text, reply_markup=settings_menu())
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "settings_level", AuthorizedCallback(ALLOWED_USERS))
async def settings_level_show(callback: CallbackQuery):
    uid = callback.from_user.id
    level_icon = LEVEL_NAMES.get(get_level(uid), get_level(uid))
    text = f"📊 <b>Level</b>\n\nHozirgi: {level_icon}\n\nYangi darajani tanlang:"
    try:
        await callback.message.edit_text(text, reply_markup=level_menu())
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "settings_model", AuthorizedCallback(ALLOWED_USERS))
async def settings_model_show(callback: CallbackQuery):
    uid = callback.from_user.id
    model_icon = AVAILABLE_MODELS.get(get_model(uid), get_model(uid))
    text = f"🧠 <b>Model</b>\n\nHozirgi: {model_icon}\n\nYangi modelni tanlang:"
    try:
        await callback.message.edit_text(text, reply_markup=model_menu())
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data == "settings_main", AuthorizedCallback(ALLOWED_USERS))
async def settings_back(callback: CallbackQuery):
    await settings_show(callback)


@router.callback_query(F.data.startswith("level_"), AuthorizedCallback(ALLOWED_USERS))
async def level_select(callback: CallbackQuery):
    level = callback.data.replace("level_", "")
    set_level(callback.from_user.id, level)
    name = LEVEL_NAMES.get(level, level)
    try:
        await callback.message.edit_text(
            f"✅ Daraja o'rnatildi: <b>{name}</b>",
            reply_markup=level_menu(),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()


@router.callback_query(F.data.startswith("model_"), AuthorizedCallback(ALLOWED_USERS))
async def model_select(callback: CallbackQuery):
    model = callback.data.replace("model_", "")
    set_model(callback.from_user.id, model)
    name = AVAILABLE_MODELS.get(model, model)
    try:
        await callback.message.edit_text(
            f"✅ Model o'rnatildi: <b>{name}</b>",
            reply_markup=model_menu(),
        )
    except TelegramBadRequest as e:
        if "message is not modified" not in str(e):
            raise
    await callback.answer()

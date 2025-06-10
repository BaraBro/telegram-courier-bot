# keyboards.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

def get_status_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🏠 База", callback_data="status_base"),
        InlineKeyboardButton("🚚 Уехал", callback_data="status_away"),
        InlineKeyboardButton("🔧 Сломался", callback_data="status_broke"),
        InlineKeyboardButton("📋 По делам", callback_data="status_busy"),
        InlineKeyboardButton("⛽ Заправка", callback_data="status_fuel"),
    )
    return kb

def get_location_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton("Отправить локацию", request_location=True))
    return kb

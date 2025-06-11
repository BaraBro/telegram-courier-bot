# keyboards.py

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_status_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🏠 База", callback_data="status_base"),
            InlineKeyboardButton(text="🚚 Уехал", callback_data="status_away"),
        ],
        [
            InlineKeyboardButton(text="🔧 Сломался", callback_data="status_broke"),
            InlineKeyboardButton(text="📋 По делам", callback_data="status_busy"),
        ],
        [
            InlineKeyboardButton(text="⛽ Заправка", callback_data="status_fuel"),
        ]
    ])

# ✅ Обновлённый вариант с keyboard=[[]]
location_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Отправить локацию", request_location=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

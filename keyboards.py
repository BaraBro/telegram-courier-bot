# keyboards.py

from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# ─── INLINE-СТАТУСЫ ──────────────────────────────────────
STATUS_BUTTONS = [
    ("🏠 База",     "status_base"),
    ("🚚 Уехал",    "status_away"),
    ("🔧 Сломался", "status_broke"),
    ("📋 По делам", "status_errands"),
    ("⛽ Заправка", "status_fuel"),
]

def get_status_keyboard() -> InlineKeyboardMarkup:
    """
    Inline-клавиатура:
    по 2 кнопки в ряд, пять статусов.
    """
    builder = InlineKeyboardBuilder()
    for text, cb in STATUS_BUTTONS:
        builder.button(text=text, callback_data=cb)
    builder.adjust(2)
    return builder.as_markup()

# ─── REPLY-ЛОКАЦИЯ ────────────────────────────────────────
def get_location_keyboard() -> ReplyKeyboardMarkup:
    """
    Однократная reply-клавиатура:
    📍 «Поделиться местоположением»
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Поделиться местоположением", request_location=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


# handlers/callbacks.py

import logging
from aiogram import Router, types, Bot
from aiogram.filters.text import Text

import config
from keyboards import get_status_keyboard
from core.database import Database
from utils.time_utils import in_work_time

router = Router()
logger = logging.getLogger(__name__)
db = Database()

@router.callback_query(Text(startswith="status_"))
async def on_status_callback(cq: types.CallbackQuery, bot: Bot):
    user = cq.from_user

    # Проверка прав
    if user.id not in config.AUTHORIZED_IDS:
        return await cq.answer("❌ У вас нет прав для этой операции.", show_alert=True)

    # Проверка рабочего времени
    if not in_work_time():
        return await cq.answer(
            f"⏰ Кнопки активны с {config.WORK_START_STR} до {config.WORK_END_STR} ({config.TIMEZONE}).",
            show_alert=True
        )

    key = cq.data.split("status_", 1)[1]
    labels = {
        "base": "🏠 База",
        "away": "🚚 Уехал",
        "broke": "🔧 Сломался",
        "busy": "📋 По делам",
        "fuel": "⛽ Заправка",
    }
    status_label = labels.get(key, key)

    # Сохранить в БД
    db.save_status(user.id, status_label)
    logger.info(f"User {user.id} set status {status_label}")

    # Подтверждение пользователю
    await cq.answer(f"✅ Статус сохранён: {status_label}", show_alert=False)

    # Публикация в групповой чат
    await bot.send_message(
        config.GROUP_CHAT_ID,
        f"{user.full_name} — {status_label}",
        reply_markup=get_status_keyboard()
    )

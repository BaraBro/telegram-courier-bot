# handlers/callbacks.py

import logging
from datetime import datetime

import pytz
from aiogram import Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

import config
from core.database import load_statuses, save_statuses
from utils.time_utils import in_work_time
from keyboards import get_status_keyboard

router = Router()
logger = logging.getLogger(__name__)

@router.callback_query()
async def process_callback(query: CallbackQuery):
    user = query.from_user
    key  = query.data
    logger.info(f"Callback {key} от {user.id} ({user.full_name})")

    if user.id not in config.AUTHORIZED_IDS:
        return await query.answer("❌ Нет прав", show_alert=True)
    if not in_work_time():
        return await query.answer(
            f"⏰ Доступно {config.WORK_START_STR}–{config.WORK_END_STR}", show_alert=True
        )

    mapping = {
        "status_base":    ("🏠", "База"),
        "status_away":    ("🚚", "Уехал"),
        "status_broke":   ("🔧", "Сломался"),
        "status_errands": ("📋", "По делам"),
        "status_fuel":    ("⛽", "Заправка"),
    }
    if key not in mapping:
        return await query.answer()

    emoji, text = mapping[key]
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz).strftime("%H:%M")

    # Сохраняем
    data = load_statuses()
    data[str(user.id)] = {
        "status": text,
        "full_name": user.full_name,
        "timestamp": datetime.now(tz).isoformat()
    }
    save_statuses(data)

    # Публикация
    public = f"{emoji} <b>{user.full_name}</b> «{text}» ({now})"
    await query.bot.send_message(config.GROUP_CHAT_ID, public, parse_mode="HTML")

    # Обновляем клавиатуру (если меняется)
    try:
        await query.message.edit_reply_markup(reply_markup=get_status_keyboard())
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.debug("Клавиатура без изменений, пропускаю edit.")
        else:
            raise

    await query.answer("Статус обновлён")



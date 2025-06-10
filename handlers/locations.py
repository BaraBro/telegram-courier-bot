# handlers/locations.py

import logging
from datetime import datetime

import pytz
from aiogram import Router, types
from aiogram.types import ReplyKeyboardRemove

import config
from core.database import load_statuses, save_statuses
from utils.time_utils import in_work_time
from keyboards import get_location_keyboard

router = Router()
logger = logging.getLogger(__name__)

@router.message(lambda m: m.location is not None)
async def handle_location(message: types.Message):
    user = message.from_user
    logger.info(f"Геолокация от {user.id} ({user.full_name})")

    if user.id not in config.AUTHORIZED_IDS:
        return await message.reply("❌ Нет прав.")
    if not in_work_time():
        return await message.reply("⏰ Локация только 06:55–00:45.")

    tz = pytz.timezone(config.TIMEZONE)
    now_iso = datetime.now(tz).isoformat()

    data = load_statuses()
    data[str(user.id)] = {
        "status": "База",
        "full_name": user.full_name,
        "timestamp": now_iso
    }
    save_statuses(data)

    lat, lon = message.location.latitude, message.location.longitude
    await message.bot.send_message(
        config.GROUP_CHAT_ID,
        f"📍 <b>{user.full_name}</b> местоположение: {lat:.5f}, {lon:.5f}",
        parse_mode="HTML"
    )
    await message.reply(
        "✅ Статус «База» подтверждён.",
        reply_markup=ReplyKeyboardRemove()
    )

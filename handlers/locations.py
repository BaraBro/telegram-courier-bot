# handlers/locations.py

import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

import config
from core.database import Database
from utils.time_utils import in_work_time

router = Router()
logger = logging.getLogger(__name__)
db = Database()

@router.message(content_types=types.ContentType.LOCATION)
async def on_location(message: types.Message, bot: Bot):
    user = message.from_user

    if user.id not in config.AUTHORIZED_IDS:
        return await message.reply("❌ У вас нет прав.")

    if not in_work_time():
        return await message.reply(
            f"⏰ Кнопки работают с {config.WORK_START_STR} до {config.WORK_END_STR} ({config.TIMEZONE})"
        )

    loc = message.location
    db.save_location(user.id, loc.latitude, loc.longitude, period="По умолчанию")

    await message.reply("✅ Локация сохранена!")

    # Публикация в группе
    await bot.send_message(
        config.GROUP_CHAT_ID,
        f"📍 {user.full_name} сообщил координаты:\n"
        f"<code>{loc.latitude}, {loc.longitude}</code>"
    )

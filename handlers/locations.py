# handlers/locations.py

import logging
from aiogram import Router, types, Bot

import config
from core.database import Database
from keyboards import location_kb
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
            f"⏰ Кнопки работают с {config.WORK_START_STR} до {config.WORK_END_STR} ({config.TIMEZONE})."
        )

    loc = message.location
    # Здесь period можно расширить через FSM; пока дефолт
    db.save_location(user.id, loc.latitude, loc.longitude, period="default")

    await message.reply("✅ Локация сохранена!")

    await bot.send_message(
        config.GROUP_CHAT_ID,
        f"📍 {user.full_name} — <code>{loc.latitude}, {loc.longitude}</code>"
    )

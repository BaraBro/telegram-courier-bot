# bot.py

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ChatMemberUpdated
from keyboards import get_status_keyboard

import config
from utils.logger import setup_logger
from handlers.commands import router as commands_router, build_welcome_text
from handlers.callbacks import router as callbacks_router
from handlers.locations import router as locations_router
from core.database import load_statuses

# ─── Настройка логгера ─────────────────────────────────────
setup_logger()
logger = logging.getLogger(__name__)

# ─── Проверка конфигурации ──────────────────────────────────
if not load_statuses():
    logger.warning("⚠️ Не удалось загрузить статусы, будет использоваться пустой словарь.")

# ─── Инициализация бота и диспетчера ──────────────────────
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
dp = Dispatcher(storage=MemoryStorage())

# ─── Регистрация роутеров ──────────────────────────────────
dp.include_router(commands_router)
dp.include_router(callbacks_router)
dp.include_router(locations_router)

# ─── Главная корутина ──────────────────────────────────────
async def main():
    logger.info("🚀 Бот запускается…")
    await dp.start_polling(bot, skip_updates=True)
    
@dp.my_chat_member()
async def on_bot_added_to_group(update: ChatMemberUpdated):
    old, new = update.old_chat_member.status, update.new_chat_member.status
    # Когда бот получил админ
    if old in ("member","restricted") and new in ("administrator",):
        chat_id = update.chat.id
        text = build_welcome_text()
        sent = await bot.send_message(
            chat_id,
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=get_status_keyboard()
        )
        try:
            await bot.pin_chat_message(chat_id, sent.message_id, disable_notification=True)
        except Exception:
            pass

# ─── Точка входа ──────────────────────────────────────────
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("🛑 Бот остановлен")

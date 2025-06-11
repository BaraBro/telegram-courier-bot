# handlers/commands.py

import logging

from aiogram import Router, types, Bot
from aiogram.filters import Command

import config
from keyboards import get_status_keyboard
from utils.status_manager import StatusManager
from core.database import Database

router = Router()
logger = logging.getLogger(__name__)
db = Database()

def build_welcome_text() -> str:
    return (
        "<b>🤖 AutoCouriersStatusBot</b>\n\n"
        "👋 Привет! Я — бот для отслеживания статусов курьеров.\n\n"
        "➡️ В групповом чате нажмите одну из кнопок:\n"
        "   🏠 «База»      — вы на складе;\n"
        "   🚚 «Уехал»     — вы отсутствуете;\n"
        "   🔧 «Сломался»  — у вас поломка;\n"
        "   📋 «По делам»  — вы заняты;\n"
        "   ⛽ «Заправка»  — вы на заправке.\n\n"
        f"⏰ Кнопки активны с {config.WORK_START_STR} до {config.WORK_END_STR} ({config.TIMEZONE}).\n\n"
        "В личном чате доступны команды:\n"
        "  • /status — узнать, кто сейчас на базе;\n"
        "  • /help   — получить инструкцию."
    )

async def ensure_started(message: types.Message) -> bool:
    uid = message.from_user.id
    if not db.has_started(uid):
        await message.reply("⚠️ Пожалуйста, сначала нажмите /start.")
        return False
    return True

@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot):
    db.set_started(message.from_user.id)
    logger.info(f"/start от {message.from_user.id}")
    text = build_welcome_text()
    if message.chat.type in ("group", "supergroup"):
        await message.answer(text, reply_markup=get_status_keyboard())
    else:
        await message.answer(text)

@router.message(Command("help"))
async def cmd_help(message: types.Message, bot: Bot):
    if not await ensure_started(message):
        return

    HELP_TEXT = (
        "📖 *Инструкция AutoCouriers StatusBot*\n\n"
        "1️⃣ В группе жмите кнопки статусов:\n"
        "   🏠 База, 🚚 Уехал, 🔧 Сломался,\n"
        "   📋 По делам, ⛽ Заправка\n\n"
        "2️⃣ При первом «База» бот попросит локацию.\n"
        "3️⃣ /status выдаёт полный отчёт в личку.\n"
        f"4️⃣ Кнопки активны с {config.WORK_START_STR} до {config.WORK_END_STR}."
    )
    try:
        await bot.send_message(message.from_user.id, HELP_TEXT, parse_mode="Markdown")
        await message.reply("✅ Инструкция отправлена в ЛС.")
    except:
        await message.reply("❗ Откройте ЛС со мной и повторите /help.")

@router.message(Command("status"))
async def cmd_status(message: types.Message, bot: Bot):
    if not await ensure_started(message):
        return

    if message.from_user.id not in config.AUTHORIZED_IDS:
        return await message.reply("❌ У вас нет прав для этой команды.")
    report = StatusManager().get_report()
    try:
        await bot.send_message(message.from_user.id, report, parse_mode="HTML")
        await message.reply("✅ Статус отправлен в ЛС.")
    except:
        await message.reply("❗ Откройте ЛС со мной и повторите /status.")

# handlers/commands.py

import logging
from aiogram import Router, types, Bot
from aiogram.filters import Command

import config
from keyboards import get_status_keyboard
from utils.time_utils import in_work_time
from core.database import load_statuses
from utils.status_manager import StatusManager


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
        "В личном чате со мной доступны команды:\n"
        "  • /status — узнать, кто сейчас на базе;\n"
        "  • /help   — получить инструкцию."
    )

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot):
    """Приветствие и клавиатура в группе / текст в ЛС."""
    user = message.from_user
    logger.info(f"/start от {user.id} ({user.full_name})")
    text = build_welcome_text()
    if message.chat.type in ("group", "supergroup"):
        await message.answer(text, reply_markup=get_status_keyboard())
    else:
        await message.answer(text)

@router.message(Command("help"))
async def cmd_help(message: types.Message, bot: Bot):
    """Инструкция, отправляемая в ЛС."""
    text = (
        "📖 *Инструкция AutoCouriers StatusBot*\n\n"
        "1️⃣ В группе жмите кнопки:\n"
        "   🏠 База, 🚚 Уехал, 🔧 Сломался,\n"
        "   📋 По делам, ⛽ Заправка\n\n"
        "2️⃣ При первом «База» выскочит запрос локации.\n"
        "3️⃣ Команда /status в ЛС выдаёт полный отчёт.\n"
        "4️⃣ Кнопки работают с 06:55 до 00:45."
    )
    success = await bot.send_message(message.from_user.id, text, parse_mode="Markdown")
    if not success:
        await message.reply("Откройте ЛС и напишите /help мне лично.")

@router.message(Command("status"))
async def cmd_status(message: types.Message, bot: Bot):
    """Послать пользователю в ЛС подробный отчёт статусов."""
    user = message.from_user
    if user.id not in config.AUTHORIZED_IDS:
        return await message.reply("❌ Нет прав.")
    report = StatusManager().get_report()
    success = await bot.send_message(user.id, report, parse_mode="HTML")
    if success:
        await message.reply("✅ Статус отправлен в ЛС.")
    else:
        await message.reply("❗ Откройте личку ботa и повторите /status.")

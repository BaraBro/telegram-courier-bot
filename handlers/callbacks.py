# handlers/callbacks.py
import logging
from typing import Optional
from aiogram import Router, types, Bot
from aiogram.exceptions import TelegramBadRequest
from config import TIMEZONE, AUTHORIZED_IDS, GROUP_CHAT_ID, WORK_START_STR, WORK_END_STR
from keyboards import get_status_keyboard
from core.database import Database
from utils.time_utils import in_work_time
from utils.status_manager import StatusManager

router = Router()
logger = logging.getLogger(__name__)
db = Database()

@router.callback_query(lambda cq: cq.data == "show_help")
async def show_help_popup(cq: types.CallbackQuery, bot: Bot):
    if not in_work_time():
        return await cq.answer(
            f"⏰ Кнопки активны с {WORK_START_STR} до {WORK_END_STR} ({TIMEZONE}).",
            show_alert=True
        )
    
    HELP_TEXT = (
        "🚀 AutoCouriersStatusBot 🚀\n\n"
        "• Отслеживает статусы курьеров\n"
        "• Присылает отчёты в личку\n"
        "• Отправляет больше информации через /help\n\n"
        f"⏰ Статусы активны с {WORK_START_STR} до {WORK_END_STR} ({TIMEZONE})"
    )
    
    try:
        await cq.answer(HELP_TEXT, show_alert=True)
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.debug("Клавиатура не изменилась, пропускаю.")
        else:
            logger.error(f"Telegram API ошибка: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)

@router.callback_query(lambda cq: cq.data == "show_status")
async def show_status_popup(cq: types.CallbackQuery, bot: Bot):
    if not GROUP_CHAT_ID or GROUP_CHAT_ID == 0:
        logger.warning("❌ GROUP_CHAT_ID не задан в .env")
        return await cq.answer("⚠️ GROUP_CHAT_ID не задан в конфиге.", show_alert=True)
    
    try:
        report = StatusManager().get_report()
        await cq.answer("✅ Отправляю отчёт в ЛС…", show_alert=True)
        await bot.send_message(cq.from_user.id, report, parse_mode="HTML")
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            logger.debug("Клавиатура не изменилась, пропускаю edit.")
        else:
            logger.error(f"Telegram API ошибка: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)

@router.callback_query(lambda cq: cq.data.startswith("status_"))
async def on_status_callback(cq: types.CallbackQuery, bot: Bot):
    user = cq.from_user
    if user.id not in AUTHORIZED_IDS:
        return await cq.answer("❌ У вас нет прав изменять статус.", show_alert=True)
    
    if not in_work_time():
        return await cq.answer(
            f"⏰ Кнопки активны с {WORK_START_STR} до {WORK_END_STR} ({TIMEZONE}).",
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
    
    try:
        db.save_status(user.id, status_label)
        logger.info(f"User {user.id} set status {status_label}")
    except Exception as e:
        logger.error(f"❌ Ошибка сохранения статуса пользователя {user.id}: {e}")
        return await cq.answer("⚠️ Ошибка сохранения статуса.", show_alert=True)
    
    try:
        await bot.send_message(
            chat_id=GROUP_CHAT_ID,
            text=f"{user.full_name} — {status_label}",
            parse_mode="HTML"
        )
    except TelegramBadRequest as e:
        logger.error(f"Telegram API ошибка: {e}", exc_info=True)
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}", exc_info=True)
    
    await cq.answer(f"✅ Статус сохранён: {status_label}", show_alert=True)
    
@router.callback_query(lambda cq: cq.data == "lighthouse")
async def on_lighthouse(cq: types.CallbackQuery):
    await cq.answer(
        "📞 Клиент Татьяна: +79857212682\n"
        "📍 Лайт Хаус 28 — вне очереди, везём сразу!!!",
        show_alert=True
    )
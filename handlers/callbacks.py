# handlers/callbacks.py

import logging
import time
from aiogram import Router, types, Bot

import config
from keyboards import get_status_keyboard
from core.database import Database
from utils.time_utils import in_work_time
from utils.status_manager import StatusManager

router = Router()
logger = logging.getLogger(__name__)
db = Database()


@router.callback_query(lambda cq: cq.data == "show_help")
async def show_help_popup(cq: types.CallbackQuery, bot: Bot):
    # Сокращённое всплывающее окно (не больше 2000 символов)
    HELP_TEXT = (
        "🚀 *AutoCouriersStatusBot*  \n"
        "• Отслеживает статусы курьеров  \n"
        "• Присылает отчёты в личку  \n\n"
        "⏰ Статусы активны с "
        f"{config.WORK_START_STR} до {config.WORK_END_STR} ({config.TIMEZONE})"
    )
    await cq.answer(HELP_TEXT, show_alert=True)


@router.callback_query(lambda cq: cq.data == "show_status")
async def show_status_popup(cq: types.CallbackQuery, bot: Bot):
    report = StatusManager().get_report()  # убрали as_table
    await cq.answer("✅ Отправляю вам отчёт в ЛС…", show_alert=True)
    await bot.send_message(cq.from_user.id, report, parse_mode="HTML")


@router.callback_query(lambda cq: cq.data is not None and cq.data.startswith("status_"))
async def on_status_callback(cq: types.CallbackQuery, bot: Bot):
    user = cq.from_user

    # Проверка рабочего времени
    if not in_work_time():
        return await cq.answer(
            f"⏰ Кнопки активны с {config.WORK_START_STR} до {config.WORK_END_STR} ({config.TIMEZONE}).",
            show_alert=True
        )

    # Разбор callback_data
    key = cq.data.split("status_", 1)[1]
    labels = {
        "base": "🏠 База",
        "away": "🚚 Уехал",
        "broke": "🔧 Сломался",
        "busy": "📋 По делам",
        "fuel": "⛽ Заправка",
    }
    status_label = labels.get(key, key)

    # Сохранить в БД с таймштампом и именем
    db.save_status(user.id, status_label)  # передаём только id и статус
    logger.info(f"User {user.id} set status {status_label}")

    # Подтверждение пользователю
    await cq.answer(f"✅ Статус сохранён: {status_label}", show_alert=True)

    # Публикация в общем чате — без клавиатуры
    await bot.send_message(
        config.GROUP_CHAT_ID,
        f"{user.full_name} — {status_label}"
    )

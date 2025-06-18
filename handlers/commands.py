# handlers/commands.py

import logging
import time
from aiogram import Router, types, Bot
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.enums.chat_type import ChatType
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, PROMOTED_TRANSITION

import config
from keyboards import get_status_keyboard
from utils.status_manager import StatusManager
from core.database import Database
from utils.time_utils import get_shift_start_timestamp

import re

router = Router()
logger = logging.getLogger(__name__)
db = Database()

# список ключевых слов (регистр не важен)
BAD_WORDS = ["база", "baza", "base", "uehal", "uexal", "yehal", "yexal", "уехал", "по делам", "заправка", "azs", "azc", "азс"]

@router.message(lambda m: isinstance(m.text, str) and any(
    re.search(rf"\b{w}\b", m.text, re.IGNORECASE) for w in BAD_WORDS
))
async def catch_free_text(m: types.Message, bot: Bot):
    """
    Если участник пишет одно из слов вместо нажатия кнопки —
    удаляем, сохраняем статус и публикуем «нормальное» сообщение.
    """
    user = m.from_user
    text = m.text.strip().lower()
    # находим ближайший ключ
    for w in BAD_WORDS:
        if re.search(rf"\b{w}\b", text):
            keyword = w
            break
    labels = {
        "база":     "🏠 База",
        "baza":     "🏠 База",
        "base":     "🏠 База",
        "уехал":    "🚚 Уехал",
        "uehal":    "🚚 Уехал",
        "uexal":    "🚚 Уехал",
        "yehal":    "🚚 Уехал",
        "yexal":    "🚚 Уехал",
        "сломался": "🔧 Сломался",
        "по делам": "📋 По делам",
        "заправка": "⛽ Заправка",
        "азс":      "⛽ Заправка",
        "azc":      "⛽ Заправка",
        "azs":      "⛽ Заправка",
    }
    status_label = labels.get(keyword, keyword)
    # удаляем сообщение
    await m.delete()
    # сохраняем в БД
    db.save_status(user.id, status_label)
    # публикуем в чат
    await bot.send_message(
        m.chat.id,
        f"{user.full_name} — {status_label}"
    )
    return

@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=PROMOTED_TRANSITION)
)
async def on_bot_promoted(my_chat_member: types.ChatMemberUpdated, bot: Bot):
    """
    Когда бот получает админ‑права в групповом чате —
    автоматически шлём и пиним главное сообщение.
    """
    chat_id = my_chat_member.chat.id
    text = build_welcome_text()
    sent = await bot.send_message(chat_id, text, reply_markup=build_welcome_buttons())
    try:
        await bot.unpin_chat_message(chat_id)
    except:
        pass
    await bot.pin_chat_message(chat_id, sent.message_id)

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
        "👇 Ниже — быстрый доступ к помощи и отчёту:"
    )

def build_welcome_buttons() -> InlineKeyboardMarkup:
    """
    Собирает общий inline-кейс: первая строка —
    кнопки «Инструкция»/«Статус», далее —
    строки из get_status_keyboard().
    """
    status_kb = get_status_keyboard()
    if not status_kb.inline_keyboard:
        logger.warning("Клавиатура статусов не создана")
        status_rows = []
    else:
        status_rows = status_kb.inline_keyboard

    header = [
        InlineKeyboardButton(text="📖 Инструкция", callback_data="show_help"),
        InlineKeyboardButton(text="📋 Статус",      callback_data="show_status"),
        InlineKeyboardButton(text="⛴ Лайт Хаус 28", callback_data="lighthouse"),
    ]
    all_rows = [header] + status_rows
    return InlineKeyboardMarkup(inline_keyboard=all_rows)

async def ensure_started(message: types.Message) -> bool:
    uid = message.from_user.id
    if not db.has_started(uid):
        await message.reply("⚠️ Пожалуйста, сначала нажмите /start.")
        return False
    return True

@router.message(Command("start"))
async def cmd_start(message: types.Message, bot: Bot):
    # Удаляем команду сразу
    await message.delete()

    # Групповой чат: один /start за смену
    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        now_ts = time.time()
        shift_start_ts = get_shift_start_timestamp()
        last_ts = db.get_global_start()

        if last_ts is None or last_ts < shift_start_ts:
            # Первый /start после начала смены
            db.set_global_start(now_ts)
            db.set_started(message.from_user.id)
            logger.info(f"Первый /start за смену от {message.from_user.id}")

            text = build_welcome_text()
            sent = await message.answer(text, reply_markup=build_welcome_buttons())
            # Пере-пин сообщения
            try:
                await bot.unpin_chat_message(message.chat.id)
                await bot.pin_chat_message(message.chat.id, sent.message_id)
            except Exception:
                pass
        # иначе — игнорируем
        return

    # ЛС: проверяем членство в группе
    if message.chat.type == ChatType.PRIVATE:
        try:
            member = await bot.get_chat_member(config.GROUP_CHAT_ID, message.from_user.id)
        except Exception:
            member = None
        if not member or member.status in ("left", "kicked"):
            # отказ «случайному прохожему»
            await message.reply("❌ Доступ к боту только для участников рабочего чата.")
            return
        # участник группы — показываем приветствие
        text = build_welcome_text()
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="📖 Инструкция", callback_data="show_help"),
            InlineKeyboardButton(text="📋 Статус",       callback_data="show_status"),
            InlineKeyboardButton(text="⛴ Lighthouse 28", callback_data="lighthouse"),
        ]])
        await message.answer(text, reply_markup=kb)
        return

    # прочие типы чатов — игнорируем

# ——— Перехват /help в группе — показываем алерт и удаляем команду ———
@router.message(Command("help"), lambda m: m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP))
async def _help_group(m: types.Message, bot: Bot):
    await m.delete()
    await m.answer("⚠️ Нажмите кнопку «📖 Инструкция», чтобы получить помощь.")

@router.message(Command("help"))
async def cmd_help(message: types.Message, bot: Bot):
    if not await ensure_started(message):
        return

    HELP_TEXT = (
        "<b>🚀 Добро пожаловать в AutoCouriersStatusBot!</b>\n\n"
        "🔍 *Основные возможности:*\n"
        "   • 📋 Отслеживать статусы всех курьеров в режиме реального времени;\n"
        "   • 🚀 Моментально отправлять и получать отчёты в личные сообщения;\n"
        "   • 🔔 Popup-уведомления об обновлениях — никаких лишних сообщений в чате;\n\n"
        "🔥 *Как начать:* \n"
        "1️⃣ Нажмите «📖 Инструкция» в этом сообщении, чтобы увидеть это окно.\n"
        "2️⃣ В любое время нажмите кнопку «📋 Статус», чтобы получить актуальный отчёт.\n"
        "3️⃣ Нажмите кнопку «🏠 База», чтобы начать смену и обновить свой статус.\n\n"
        "🏁 *Команды на личной переписке:* \n"
        "  • /status — полный отчёт по статусам;\n"
        "  • /help   — снова показать справку.\n\n"
        f"⏰ Кнопки статусов доступны с {config.WORK_START_STR} до {config.WORK_END_STR} ({config.TIMEZONE}).\n"
        "🕒 В 01:00 статусы автоматически сбрасываются, и вы начнёте новую смену c 07:00."
    )

    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        try:
            await bot.send_message(message.from_user.id, HELP_TEXT, parse_mode="HTML")
            await message.reply("✅ Инструкция отправлена в ЛС.", show_alert=True)
        except Exception as e:
            logger.error(f"Не удалось отправить ЛС пользователю {message.from_user.id}: {e}")
            await message.reply("❗ Откройте ЛС со мной и повторите /help.")
        return

    await message.answer(HELP_TEXT, parse_mode="HTML")

# ——— Перехват /status в группе — показываем алерт и удаляем команду ———
@router.message(Command("status"), lambda m: m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP))
async def _status_group(m: types.Message, bot: Bot):
    await m.delete()
    await m.answer("⚠️ Нажмите кнопку «📋 Статус», чтобы получить отчёт.")

@router.message(Command("status"))
async def cmd_status(message: types.Message, bot: Bot):
    # В группе — предложить нажать кнопку
    if message.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        await message.delete()
        await message.answer("⚠️ Нажмите кнопку «📋 Статус» ниже.")
        return

    # В ЛС — любой может запросить отчёт
    report = await StatusManager().get_report(bot)
    await message.answer(report, parse_mode="HTML")

# handlers/locations.py

import logging
import time

from aiogram import Router, types, Bot
from aiogram import F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
)

import config
from core.database import Database
from utils.time_utils import in_work_time, get_shift_start_timestamp
from states import LocationStates

logger = logging.getLogger(__name__)
db = Database()
router = Router()


def build_period_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="15 мин", callback_data="period_15")],
        [InlineKeyboardButton(text="1 ч",   callback_data="period_60")],
        [InlineKeyboardButton(text="6 ч",   callback_data="period_360")],
        [InlineKeyboardButton(text="8 ч",   callback_data="period_480")],
    ])


@router.callback_query(lambda cq: cq.data == "status_base")
async def on_base(cq: types.CallbackQuery, state: FSMContext, bot: Bot):
    # сброс при первой базе после начала смены
    now = int(time.time())
    shift0 = get_shift_start_timestamp()
    if db.get_last_reset() < shift0:
        db.reset_statuses()

    if not in_work_time():
        return await cq.answer("⏰ Не в рабочее время.", show_alert=True)

    await cq.answer("Выберите, как долго вы будете на базе:", show_alert=False)
    await state.set_state(LocationStates.waiting_period)
    await bot.send_message(
        cq.from_user.id,
        "Пожалуйста, выберите период наблюдения:",
        reply_markup=build_period_keyboard()
    )


@router.callback_query(
    StateFilter(LocationStates.waiting_period),
    lambda cq: cq.data.startswith("period_")
)
async def on_period_chosen(cq: types.CallbackQuery, state: FSMContext, bot: Bot):
    period = cq.data.split("_", 1)[1]  # "15", "60", ...
    await state.update_data(period=period)

    await cq.answer("Отлично! Теперь пришлите свою геолокацию.", show_alert=True)
    await state.set_state(LocationStates.waiting_location)
    await bot.send_message(
        cq.from_user.id,
        "Нажмите кнопку для отправки геолокации:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отправить локацию", request_location=True)]],
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


@router.message(StateFilter(LocationStates.waiting_location), F.content_type == "location")
async def process_location(message: types.Message, state: FSMContext):
    data = await state.get_data()
    period = data.get("period", "unknown")
    lat = message.location.latitude
    lon = message.location.longitude

    db.save_location(message.from_user.id, lat, lon, period)
    logger.info(f"Сохранил локацию {message.from_user.id}: {lat},{lon} на {period} мин")

    await message.bot.send_message(
        chat_id=config.GROUP_CHAT_ID,
        text=(
            f"{message.from_user.full_name} на базе ({period} мин) — "
            f"📍 {lat:.4f}, {lon:.4f}"
        )
    )

    await state.clear()
    await message.answer(
        "✅ Локация сохранена, статус в группе обновлён.",
        reply_markup=ReplyKeyboardRemove()
    )

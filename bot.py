# bot.py

import logging
from aiogram import Bot, Dispatcher, types
from aiogram.client.default import DefaultBotProperties
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter
from aiogram.enums.chat_member_status import ChatMemberStatus

import config
from handlers.commands import router as commands_router, build_welcome_text
from handlers.callbacks import router as callbacks_router
from handlers.locations import router as locations_router
from keyboards import get_status_keyboard

logger = logging.getLogger(__name__)

async def on_bot_added_to_group(event: types.ChatMemberUpdated, bot: Bot):
    if event.new_chat_member.status == ChatMemberStatus.MEMBER:
        text = build_welcome_text()
        await bot.send_message(
            chat_id=event.chat.id,
            text=text,
            reply_markup=get_status_keyboard()
        )
        try:
            await bot.pin_chat_message(
                chat_id=event.chat.id,
                message_id=event.related_message.message_id
            )
        except Exception:
            pass

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    bot = Bot(
        token=config.TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    dp.include_router(commands_router)
    dp.include_router(callbacks_router)
    dp.include_router(locations_router)

    logger.info("🚀 Bot started")
    dp.run_polling(bot)

if __name__ == "__main__":
    main()

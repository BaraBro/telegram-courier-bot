# bot.py

import logging
from aiogram import Bot, Dispatcher, types
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
        chat = event.chat
        text = build_welcome_text()
        await bot.send_message(
            chat_id=chat.id,
            text=text,
            reply_markup=get_status_keyboard()
        )
        try:
            await bot.pin_chat_message(chat_id=chat.id, message_id=event.message.message_id)
        except Exception:
            pass

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    bot = Bot(token=config.TOKEN, parse_mode="HTML")
    dp = Dispatcher()

    dp.include_router(commands_router)
    dp.include_router(callbacks_router)
    dp.include_router(locations_router)

    dp.on_event(
        ChatMemberUpdatedFilter(member_status_changed=ChatMemberStatus.MEMBER),
        on_bot_added_to_group
    )

    logger.info("Бот запущен")
    dp.run_polling(bot)

if __name__ == "__main__":
    main()

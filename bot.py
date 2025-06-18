# bot.py

import asyncio
import logging
import signal

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

def register_signal_handlers(loop: asyncio.AbstractEventLoop, shutdown_cb):
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown_cb(sig)))

async def shutdown(signal_received, dp: Dispatcher, bot: Bot):
    logger.info(f"Получен сигнал {signal_received.name}, начинаю shutdown…")
    # остановить polling
    await dp.stop_polling()
    # закрыть storage (если вы используете Redis/MemoryStorage)
    if dp.storage:
        await dp.storage.close()
        await dp.storage.wait_closed()
    # закрыть HTTP‑сессию бота
    await bot.session.close()
    logger.info("Бот корректно завершил работу.")
    # остановить loop
    asyncio.get_event_loop().stop()

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    bot = Bot(
        token=config.TOKEN,
        default=DefaultBotProperties(parse_mode="HTML")
    )
    dp = Dispatcher()

    # регистрация роутеров
    dp.include_router(commands_router)
    dp.include_router(callbacks_router)
    dp.include_router(locations_router)
    # регистрация автоприветствия в группу
    dp.my_chat_member.register(on_bot_added_to_group, ChatMemberUpdatedFilter(member_status_changed=ChatMemberStatus.MEMBER))

    # graceful shutdown
    loop = asyncio.get_event_loop()
    register_signal_handlers(loop, lambda sig: shutdown(sig, dp, bot))

    logger.info("🚀 Bot started")
    # Запустить polling (останавливается в shutdown)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

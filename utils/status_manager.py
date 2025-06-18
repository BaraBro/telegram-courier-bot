# utils/status_manager.py

import time
from aiogram import Bot
import config
from core.database import Database

class StatusManager:
    def __init__(self):
        self.db = Database()

    async def get_report(self, bot: Bot) -> str:
        """
        Асинхронно собрать HTML‑отчёт:
          • Имя — Статус (⏱ часы:минуты или минуты)
        Принимает существующий объект bot, чтобы не открывать новый сессию.
        """
        raw = self.db.load_statuses()  # { uid_str: {"status":…, "ts":…}, … }
        now = int(time.time())
        if not raw:
            return "ℹ️ Пока нет сохранённых статусов."

        lines = ["📋 <b>Отчёт статусов курьеров:</b>\n"]
        for uid_str, rec in raw.items():
            status = rec.get("status", "—")
            ts = rec.get("ts", now)
            elapsed = now - ts
            hours = int(elapsed // 3600)
            minutes = int((elapsed % 3600) // 60)
            timer = f"{hours:02d}:{minutes:02d}" if hours else f"{minutes:02d} мин"
            # получаем имя участника
            try:
                member = await bot.get_chat_member(config.GROUP_CHAT_ID, int(uid_str))
                name = member.user.full_name
            except:
                name = f"<code>{uid_str}</code>"
            lines.append(f"• <b>{name}</b> — {status} (⏱ {timer})")

        return "\n".join(lines)

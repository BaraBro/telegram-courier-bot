# utils/status_manager.py

from core.database import Database
from core.database import DB_FILE  # если нужно знать путь или для логирования
import logging

logger = logging.getLogger(__name__)
_db = Database()

class StatusManager:
    """Формирует отчёт по текущим статусам курьеров."""

    def __init__(self):
        # можно хранить отдельное соединение, если нужно
        self._db = _db

    def set_status(self, user_id: int, status: str) -> None:
        """
        (Если используется) Сохранить статус курьера.
        В противном случае – колбеки сами вызывают db.save_status().
        """
        self._db.save_status(user_id, status)
        logger.info(f"Status saved: user {user_id} -> {status}")

    def get_report(self) -> str:
        """
        Собрать HTML-отчёт вида:
        <b>Отчёт статусов:</b>
        • User FullName — статус
        • ...
        """
        statuses = self._db.load_statuses()  # возвращает dict[str, str]
        if not statuses:
            return "<b>Нет данных по статусам.</b>"

        parts = ["<b>📋 Отчёт статусов курьеров:</b>\n"]
        for uid_str, status in statuses.items():
            try:
                uid = int(uid_str)
                # здесь можно подтягивать user.full_name через Telegram API,
                # но для простоты оставим ID
                parts.append(f"• <code>{uid}</code> — {status}")
            except ValueError:
                parts.append(f"• {uid_str} — {status}")
        return "\n".join(parts)

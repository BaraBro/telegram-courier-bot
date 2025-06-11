# utils/status_manager.py

import logging
from core.database import Database

logger = logging.getLogger(__name__)
_db = Database()

class StatusManager:
    """Генерирует HTML-отчёт по статусам курьеров."""

    def get_report(self) -> str:
        statuses = _db.load_statuses()
        if not statuses:
            return "<b>Нет данных по статусам.</b>"

        lines = ["<b>📋 Отчёт статусов курьеров:</b>"]
        for uid, status in statuses.items():
            lines.append(f"• <code>{uid}</code> — {status}")
        return "\n".join(lines)

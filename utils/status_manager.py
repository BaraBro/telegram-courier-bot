# utils/status_manager.py

from core.database import Database
import logging

logger = logging.getLogger(__name__)
_db = Database()

class StatusManager:
    def __init__(self):
        self._db = _db

    def get_report(self) -> str:
        statuses = self._db.load_statuses()
        if not statuses:
            return "<b>Нет данных по статусам.</b>"

        lines = ["<b>📋 Отчёт статусов курьеров:</b>"]
        for uid_str, status in statuses.items():
            lines.append(f"• <code>{uid_str}</code> — {status}")
        return "\n".join(lines)

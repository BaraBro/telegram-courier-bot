import logging
import pytz
from datetime import datetime
from typing import Dict, Any
from core.database import load_statuses, save_statuses
import config

logger = logging.getLogger(__name__)

class StatusManager:
    def __init__(self):
        self._tz = pytz.timezone(config.TIMEZONE)
        self._data: Dict[str, Dict[str, Any]] = load_statuses()

    def set(self, user_id: int, status: str, full_name: str) -> None:
        ts = datetime.now(self._tz).isoformat()
        self._data[str(user_id)] = {"status": status, "full_name": full_name, "timestamp": ts}
        if not save_statuses(self._data):
            logger.error("Failed to persist status")

    def get_report(self) -> str:
        now = datetime.now(self._tz)
        groups = {k: [] for k in ("База","Уехали","Сломались","По делам","Заправка","Не вышли")}
        for uid, info in self._data.items():
            st = info["status"]
            name = info["full_name"]
            ts = info.get("timestamp")
            timer = "—"
            if ts:
                try:
                    dt = datetime.fromisoformat(ts)
                    diff = now - dt
                    h = diff.seconds//3600; m = (diff.seconds%3600)//60
                    timer = f"{h}ч {m}м"
                except: pass
            entry = f"{name} ({timer})"
            groups.get(st, groups["Не вышли"]).append(entry)
        text = "<b>Текущий статус курьеров:</b>\n\n"
        for cat, lst in groups.items():
            text += f"─ <i>{cat}</i>:\n"
            text += "   • " + "\n   • ".join(lst) if lst else "   • (нет)"
            text += "\n\n"
        return text

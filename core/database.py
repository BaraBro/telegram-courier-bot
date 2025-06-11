# core/database.py

import os
import json
import time
import shutil
from threading import Lock

from utils.encryption import encrypt, decrypt  # теперь эти имена доступны

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, "statuses.json")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

class Database:
    def __init__(self):
        self._lock = Lock()
        self._data = self._load()

    def _load(self) -> dict:
        if not os.path.exists(DB_FILE):
            data = {"statuses": {}, "locations": {}, "users_started": []}
            self._write_raw(json.dumps(data).encode())
            return data

        raw = open(DB_FILE, "rb").read()
        try:
            text = decrypt(raw, key=os.getenv("ENCRYPTION_KEY"))
        except Exception:
            text = raw.decode("utf-8")
        return json.loads(text)

    def _write_raw(self, payload: bytes) -> None:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        if os.path.exists(DB_FILE):
            # бэкапим старый файл
            backup_name = f"{int(time.time())}_statuses.json"
            shutil.copy2(DB_FILE, os.path.join(BACKUP_DIR, backup_name))
        with open(DB_FILE, "wb") as f:
            f.write(payload)

    def _save(self) -> None:
        with self._lock:
            text = json.dumps(self._data)
            encrypted = encrypt(text, key=os.getenv("ENCRYPTION_KEY"))
            self._write_raw(encrypted)

    def load_statuses(self) -> dict[str, str]:
        return self._data.get("statuses", {})

    def save_status(self, user_id: int, status: str) -> None:
        self._data.setdefault("statuses", {})[str(user_id)] = status
        self._save()

    def load_locations(self) -> dict[str, dict]:
        return self._data.get("locations", {})

    def save_location(self, user_id: int, latitude: float, longitude: float, period: str) -> None:
        self._data.setdefault("locations", {})[str(user_id)] = {
            "lat": latitude,
            "lon": longitude,
            "period": period,
            "timestamp": int(time.time())
        }
        self._save()

    def set_started(self, user_id: int) -> None:
        users = set(self._data.get("users_started", []))
        users.add(user_id)
        self._data["users_started"] = list(users)
        self._save()

    def has_started(self, user_id: int) -> bool:
        return user_id in set(self._data.get("users_started", []))

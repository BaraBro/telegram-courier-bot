# core/database.py

import os
import json
import time
import shutil
from threading import Lock

# вместо from utils.encryption import encrypt, decrypt
from utils import encryption

# Пути к файлу и директории бэкапов
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_FILE = os.path.join(BASE_DIR, "statuses.json")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")

class Database:
    def __init__(self):
        self._lock = Lock()
        self._data = self._load()

    def _load(self) -> dict:
        """Загрузить JSON (распаковать, если зашифрован), или инициализировать."""
        if not os.path.exists(DB_FILE):
            data = {"statuses": {}, "locations": {}, "users_started": []}
            # сразу создать файл
            self._write_raw(json.dumps(data).encode())
            return data

        raw = open(DB_FILE, "rb").read()
        try:
            # вызываем метод из модуля encryption
            text = encryption.decrypt(raw)
        except Exception:
            # предположим, что файл не зашифрован
            text = raw.decode("utf-8")
        return json.loads(text)

    def _write_raw(self, payload: bytes) -> None:
        """Сохранить payload в DB_FILE, предварительно забэкапив старый."""
        os.makedirs(BACKUP_DIR, exist_ok=True)
        if os.path.exists(DB_FILE):
            timestamp = int(time.time())
            backup_path = os.path.join(BACKUP_DIR, f"{timestamp}_statuses.json")
            shutil.copy2(DB_FILE, backup_path)
        with open(DB_FILE, "wb") as f:
            f.write(payload)

    def _save(self) -> None:
        """Сериализовать self._data в JSON, зашифровать и записать."""
        with self._lock:
            text = json.dumps(self._data)
            # вызываем метод из модуля encryption
            encrypted = encryption.encrypt(text)
            self._write_raw(encrypted)

    # ======== Методы для статусов курьеров ========
    def load_statuses(self) -> dict[int, str]:
        return self._data.get("statuses", {})

    def save_status(self, user_id: int, status: str) -> None:
        self._data.setdefault("statuses", {})[str(user_id)] = status
        self._save()

    # ======== Методы для локаций ========
    def load_locations(self) -> dict[int, dict]:
        return self._data.get("locations", {})

    def save_location(self, user_id: int, latitude: float, longitude: float, period: str) -> None:
        self._data.setdefault("locations", {})[str(user_id)] = {
            "lat": latitude,
            "lon": longitude,
            "period": period,
            "timestamp": int(time.time())
        }
        self._save()

    # ======== Методы для флага /start ========
    def set_started(self, user_id: int) -> None:
        users = set(self._data.get("users_started", []))
        users.add(user_id)
        self._data["users_started"] = list(users)
        self._save()

    def has_started(self, user_id: int) -> bool:
        return user_id in set(self._data.get("users_started", []))

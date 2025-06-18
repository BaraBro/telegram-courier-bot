# core/database.py

import time
import os, json, time, shutil
from threading import Lock
from utils import encryption

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
            text = encryption.decrypt(raw)
        except Exception:
            text = raw.decode("utf-8")
        return json.loads(text)

    def _write_raw(self, payload: bytes) -> None:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        if os.path.exists(DB_FILE):
            shutil.copy2(DB_FILE, os.path.join(
                BACKUP_DIR, f"{int(time.time())}_statuses.json"))
        with open(DB_FILE, "wb") as f:
            f.write(payload)

    def _save(self) -> None:
        with self._lock:
            text = json.dumps(self._data)
            encrypted = encryption.encrypt(text)
            self._write_raw(encrypted)

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

    # ======== Глобальный /start за смену ========
    def get_global_start(self) -> float | None:
        """Время последнего однократного /start за текущую смену."""
        return self._data.setdefault("meta", {}).get("global_start")

    def set_global_start(self, ts: float) -> None:
        """Записать метку времени первого /start за смену."""
        meta = self._data.setdefault("meta", {})
        meta["global_start"] = ts
        self._save()
        
    def save_status(self, user_id: int, status_label: str) -> None:
        """Сохраняем новый статус с текущей UNIX-меткой."""
        now = int(time.time())
        self._data.setdefault("statuses", {})[str(user_id)] = {
            "status": status_label,
            "ts": now
        }
        self._save()

    def load_statuses(self) -> dict[str, dict]:
        """Возвращаем { user_id: { 'status': str, 'ts': int }, … }."""
        return self._data.get("statuses", {})

    def save_status(self, user_id: int, status_label: str) -> None:
        """Сохраняем новый статус с текущей UNIX-меткой."""
        now = int(time.time())
        self._data.setdefault("statuses", {})[str(user_id)] = {
            "status": status_label,
            "ts": now
        }
        self._save()

    def load_statuses(self) -> dict[str, dict]:
        """Возвращаем {user_id: {"status":…, "ts":…}}."""
        return self._data.get("statuses", {})
    
    def get_last_reset(self) -> int:
        return self._data.get("last_reset_ts", 0)

    def set_last_reset(self, ts: int):
        self._data["last_reset_ts"] = ts
        self._save()

    def reset_statuses(self):
        self._data["statuses"] = {}
        self.set_last_reset(int(time.time()))
        
    def get_last_reset(self) -> int:
        return self._data.get("last_reset", 0)

    def reset_statuses(self) -> None:
        self._data["statuses"] = {}
        self._data["last_reset"] = int(time.time())
        self._save()
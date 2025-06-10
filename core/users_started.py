# core/users_started.py
import json
from pathlib import Path
from typing import Set

STARTED_FILE = Path("users_started.json")


def load_started_users() -> Set[int]:
    if STARTED_FILE.exists():
        try:
            data = json.loads(STARTED_FILE.read_text(encoding="utf-8"))
            return set(data)
        except Exception:
            return set()
    return set()


def save_started_users(users: Set[int]) -> None:
    STARTED_FILE.write_text(json.dumps(list(users)), encoding="utf-8")


_started = load_started_users()


def add_started(user_id: int) -> None:
    _started.add(user_id)
    save_started_users(_started)


def has_started(user_id: int) -> bool:
    return user_id in _started
# users_started.py
# Простейшее хранилище пользователей, вызвавших /start

_started = set()

def add(user_id: int) -> None:
    """Пометить, что пользователь вызвал /start."""
    _started.add(user_id)

def exists(user_id: int) -> bool:
    """Проверить, вызывал ли пользователь /start."""
    return user_id in _started

def clear() -> None:
    """Очистить все метки (для тестов или перезапуска)."""
    _started.clear()

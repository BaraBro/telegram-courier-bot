# config.py

import os
from dotenv import load_dotenv
from datetime import time, datetime
import pytz

# ─── ЗАГРУЗКА .env ───────────────────────────────────────
load_dotenv()
BOT_TOKEN     = os.getenv("BOT_TOKEN") or ""
GROUP_CHAT_ID = int(os.getenv("GROUP_CHAT_ID", "0"))

if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN не задан в .env")
if GROUP_CHAT_ID == 0:
    raise RuntimeError("❌ GROUP_CHAT_ID не задан или некорректен")

# ─── ЧАСОВОЙ ПОЯС И РАБОЧЕЕ ВРЕМЯ ─────────────────────────
TIMEZONE      = os.getenv("TIMEZONE", "Europe/Moscow")
tz            = pytz.timezone(TIMEZONE)

def _parse_hhmm(s: str) -> time:
    hh, mm = map(int, s.split(":"))
    return time(hh, mm)

WORK_START    = _parse_hhmm(os.getenv("WORK_START", "06:55"))
WORK_END      = _parse_hhmm(os.getenv("WORK_END",   "00:45"))
WORK_START_STR = WORK_START.strftime("%H:%M")
WORK_END_STR   = WORK_END.strftime("%H:%M")

def in_work_time() -> bool:
    now = datetime.now(tz).time()
    if WORK_START < WORK_END:
        return WORK_START <= now <= WORK_END
    # переход через полночь
    return now >= WORK_START or now <= WORK_END

# ─── АВТОРИЗОВАННЫЕ ──────────────────────────────────────
AUTHORIZED_IDS = [662982044, 277821395, 5272565513, 5049992114
                  ]
authorized_map = {
    662982044: "Игорь Ладохин",
    277821395: "Влад Копцев",
    5272565513: "Кирилл Фролов",
    5049992114: "Саша"
}

# ─── КЛЮЧ ШИФРОВАНИЯ ───────────────────────────────────────
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY") or None
# (Необходимо для core/database.py)


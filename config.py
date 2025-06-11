# config.py

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    bot_token: str
    encryption_key: str | None = None
    group_chat_id: int
    authorized_ids: set[int] = Field(default_factory=set)
    work_start: str
    work_end: str
    timezone: str

    @field_validator("work_start", "work_end")
    @classmethod
    def _validate_time_fmt(cls, v: str) -> str:
        parts = v.split(":")
        if len(parts) != 2 or not all(p.isdigit() for p in parts):
            raise ValueError("Время должно быть в формате HH:MM")
        hh, mm = map(int, parts)
        if not (0 <= hh <= 23 and 0 <= mm <= 59):
            raise ValueError("Часы 00–23, минуты 00–59")
        return v

try:
    settings = Settings()
except Exception as e:
    print("Ошибка в конфиге:", e)
    raise

TOKEN          = settings.bot_token
ENCRYPTION_KEY = settings.encryption_key
GROUP_CHAT_ID  = settings.group_chat_id
AUTHORIZED_IDS = settings.authorized_ids
WORK_START_STR = settings.work_start
WORK_END_STR   = settings.work_end
TIMEZONE       = settings.timezone

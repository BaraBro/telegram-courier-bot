# utils/time_utils.py

from datetime import datetime, time, timedelta
import pytz
import config

def in_work_time() -> bool:
    """
    Возвращает True, если текущее локальное время находится между work_start и work_end.
    """
    tz = pytz.timezone(config.TIMEZONE)
    now = datetime.now(tz).time()

    start_h, start_m = map(int, config.WORK_START_STR.split(":"))
    end_h, end_m = map(int, config.WORK_END_STR.split(":"))

    start = time(start_h, start_m)
    end = time(end_h, end_m)

    if start <= end:
        return start <= now <= end
    else:
        # окно пересекает полночь
        return now >= start or now <= end

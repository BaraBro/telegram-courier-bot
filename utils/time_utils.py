from datetime import datetime, time
import pytz
import config

tz = pytz.timezone(config.TIMEZONE)

def now_local() -> time:
    return datetime.now(tz).time().replace(second=0, microsecond=0)

def in_work_time() -> bool:
    now = now_local()
    start = config.WORK_START
    end   = config.WORK_END
    if start < end:
        return start <= now <= end
    return now >= start or now <= end

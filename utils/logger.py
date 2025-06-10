import os
import logging
from logging.handlers import RotatingFileHandler

def setup_logger():
    os.makedirs("logs", exist_ok=True)
    fmt = "%(asctime)s [%(levelname)s] %(module)s:%(lineno)d ▶ %(message)s"
    formatter = logging.Formatter(fmt)

    fh = RotatingFileHandler("logs/bot.log", maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
    fh.setFormatter(formatter)
    fh.setLevel(logging.INFO)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(logging.INFO)
    root.addHandler(fh)
    root.addHandler(ch)

    logging.getLogger(__name__).info("✅ Logger configured")


# tests/test_config.py

import os
import pytest
from config import BOT_TOKEN, GROUP_CHAT_ID, WORK_START, WORK_END, TIMEZONE

def test_env_vars_present():
    assert BOT_TOKEN, "BOT_TOKEN должен быть задан"
    assert isinstance(GROUP_CHAT_ID, int) and GROUP_CHAT_ID != 0

def test_work_start_end_are_time():
    from datetime import time
    assert isinstance(WORK_START, time)
    assert isinstance(WORK_END, time)

def test_timezone_string():
    assert TIMEZONE == os.getenv("TIMEZONE")

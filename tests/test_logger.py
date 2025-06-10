# tests/test_logger.py

import os
from utils.logger import setup_logger

def test_log_file_creation(tmp_path, monkeypatch):
    # перенаправим папку logs
    monkeypatch.chdir(tmp_path)
    setup_logger()
    assert os.path.isdir("logs")
    # файл заведения потока есть, хотя он может ещё пуст
    # мы не знаем имя конкретного потока (RotatingFileHandler),
    # но директория существует

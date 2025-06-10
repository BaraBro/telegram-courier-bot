# tests/test_database.py

import pytest
import json
from pathlib import Path
from core.database import load_statuses, save_statuses

TEST_FILE = Path("test_statuses.json")

@pytest.fixture(autouse=True)
def switch_db(monkeypatch, tmp_path):
    # Подменяем DB на временный файл
    from core import database
    monkeypatch.setattr(database, "STATUS_FILE", tmp_path / "statuses.json")
    monkeypatch.setattr(database, "BACKUP_FILE", tmp_path / "statuses.json.backup")
    yield

def test_load_empty(tmp_path):
    data = load_statuses()
    assert data == {}

def test_save_and_load(tmp_path):
    sample = {"1": {"status":"test"}}
    save_statuses(sample)
    assert load_statuses() == sample

def test_backup(tmp_path):
    sample1 = {"1": {"status":"first"}}
    save_statuses(sample1)
    sample2 = {"1": {"status":"second"}}
    save_statuses(sample2)

    backup_path = tmp_path / "statuses.json.backup"
    assert backup_path.exists()

    # Дешифруем и проверяем содержимое
    from config import ENCRYPTION_KEY
    from utils.encryption import decrypt_data

    encrypted = backup_path.read_bytes()
    decrypted = decrypt_data(encrypted, ENCRYPTION_KEY)
    backup = json.loads(decrypted)

    assert backup == sample1
import json
import shutil
import logging
from pathlib import Path
from typing import Dict, Any

from config import ENCRYPTION_KEY
from utils.encryption import decrypt_data, encrypt_data

logger = logging.getLogger(__name__)

STATUS_FILE = Path("statuses.json")
BACKUP_FILE = STATUS_FILE.with_suffix(".json.backup")

def load_statuses() -> Dict[str, Dict[str, Any]]:
    if not STATUS_FILE.exists():
        return {}
    raw = STATUS_FILE.read_bytes()
    # Если незашифрованный JSON
    if raw.startswith(b"{") or raw.startswith(b"["):
        try:
            return json.loads(raw.decode("utf-8"))
        except:
            logger.warning("Plain JSON parse failed, trying decrypt")
    decrypted = decrypt_data(raw, ENCRYPTION_KEY)
    if not decrypted:
        logger.warning("Decrypt returned None, loading backup")
        return _load_backup()
    try:
        return json.loads(decrypted)
    except Exception as e:
        logger.warning(f"JSON decode after decrypt failed: {e}")
        return _load_backup()

def _load_backup() -> Dict[str, Dict[str, Any]]:
    if not BACKUP_FILE.exists():
        return {}
    try:
        return json.loads(BACKUP_FILE.read_text(encoding="utf-8"))
    except Exception as e:
        logger.error(f"Backup load failed: {e}")
        return {}

def save_statuses(data: Dict[str, Dict[str, Any]]) -> bool:
    try:
        if STATUS_FILE.exists():
            shutil.copy2(STATUS_FILE, BACKUP_FILE)
        raw = json.dumps(data, ensure_ascii=False, indent=4)
        encrypted = encrypt_data(raw, ENCRYPTION_KEY)
        STATUS_FILE.write_bytes(encrypted)
        return True
    except Exception as e:
        logger.error(f"Failed to save statuses: {e}", exc_info=True)
        return False


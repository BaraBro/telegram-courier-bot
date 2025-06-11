# utils/encryption.py

import os
import base64
import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)

def generate_key_from_string(password: str, salt: bytes = None) -> bytes:
    salt = salt or os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=390000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def validate_fernet_key(key: Optional[str]) -> bool:
    if not key:
        return False
    try:
        Fernet(key.encode())
        return True
    except Exception:
        return False

def encrypt_data(data: str, key: Optional[str] = None) -> bytes:
    """
    Шифрует строку data в байты. Если key невалиден — возвращает data.encode().
    """
    if not validate_fernet_key(key):
        return data.encode("utf-8")
    return Fernet(key.encode()).encrypt(data.encode("utf-8"))

def decrypt_data(encrypted: bytes, key: Optional[str] = None) -> Optional[str]:
    """
    Расшифровывает байты encrypted. Если key невалиден — пытается .decode(),
    иначе возвращает None в случае ошибки.
    """
    if not validate_fernet_key(key):
        try:
            return encrypted.decode("utf-8")
        except Exception:
            return None
    try:
        return Fernet(key.encode()).decrypt(encrypted).decode("utf-8")
    except InvalidToken:
        logger.warning("Decrypt failed: Invalid token")
        return None
    except Exception as e:
        logger.error(f"Decrypt error: {e}")
        return None

# Алиасы для обратной совместимости с core/database.py
encrypt = encrypt_data
decrypt = decrypt_data

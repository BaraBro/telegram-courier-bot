# utils/encryption.py

from cryptography.fernet import Fernet
import config

def _get_cipher() -> Fernet | None:
    key = config.ENCRYPTION_KEY
    if not key:
        return None
    return Fernet(key)

def encrypt(data: str) -> bytes:
    cipher = _get_cipher()
    return cipher.encrypt(data.encode("utf-8")) if cipher else data.encode("utf-8")

def decrypt(token: bytes) -> str:
    cipher = _get_cipher()
    return cipher.decrypt(token).decode("utf-8") if cipher else token.decode("utf-8")

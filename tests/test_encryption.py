# tests/test_encryption.py

import pytest
import json
from utils.encryption import encrypt_data, decrypt_data, validate_fernet_key
from config import ENCRYPTION_KEY

def test_roundtrip_with_key():
    text = json.dumps({"a":1})
    enc = encrypt_data(text, ENCRYPTION_KEY)
    dec = decrypt_data(enc, ENCRYPTION_KEY)
    assert json.loads(dec) == {"a":1}

def test_no_key_passthrough():
    raw = "hello"
    enc = encrypt_data(raw, None)
    assert isinstance(enc, bytes) and enc.decode() == raw
    dec = decrypt_data(enc, None)
    assert dec == raw

def test_validate_key():
    assert validate_fernet_key(ENCRYPTION_KEY)
    assert not validate_fernet_key("bad_key")

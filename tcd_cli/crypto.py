from __future__ import annotations

import base64
import json
from typing import Any

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.padding import PKCS7

from .config import PAY_IV_B64, PAY_KEY_B64


def encrypt_payment_payload(payload: dict[str, Any]) -> str:
    """AES/CBC/PKCS7 + Base64, matches AesCrypt.encryptPayment in the app."""
    plaintext = json.dumps(payload, separators=(",", ":"), ensure_ascii=False)
    key = base64.b64decode(PAY_KEY_B64)
    iv = base64.b64decode(PAY_IV_B64)
    padder = PKCS7(128).padder()
    padded = padder.update(plaintext.encode("utf-8")) + padder.finalize()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return base64.b64encode(ciphertext).decode("ascii")

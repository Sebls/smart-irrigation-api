from __future__ import annotations

import base64
import hashlib
import hmac
import os

_ALGO = "pbkdf2_sha256"
_HASH_NAME = "sha256"
_SALT_BYTES = 16
_DK_LEN = 32
_DEFAULT_ITERATIONS = int(os.getenv("PWD_HASH_ITERATIONS", "390000"))


def hash_password(password: str) -> str:
    """
    Hash a password using PBKDF2-HMAC-SHA256 (stdlib-only, no extra deps).

    Format: pbkdf2_sha256$<iterations>$<salt_b64>$<dk_b64>
    """
    if password is None or password == "":
        raise ValueError("password must be a non-empty string")

    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac(_HASH_NAME, password.encode("utf-8"), salt, _DEFAULT_ITERATIONS, dklen=_DK_LEN)
    return (
        f"{_ALGO}"
        f"${_DEFAULT_ITERATIONS}"
        f"${base64.b64encode(salt).decode('ascii')}"
        f"${base64.b64encode(dk).decode('ascii')}"
    )


def verify_password(plain_password: str, password_hash: str) -> bool:
    try:
        algo, iterations_s, salt_b64, dk_b64 = password_hash.split("$", 3)
        if algo != _ALGO:
            return False
        iterations = int(iterations_s)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected = base64.b64decode(dk_b64.encode("ascii"))
    except Exception:
        return False

    derived = hashlib.pbkdf2_hmac(_HASH_NAME, plain_password.encode("utf-8"), salt, iterations, dklen=len(expected))
    return hmac.compare_digest(derived, expected)

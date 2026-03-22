import secrets
import hashlib
import hmac

ITERATIONS = 600_000
SALT_LENGTH = 16

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_LENGTH)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return f"{salt.hex()}:{key.hex()}"

def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt_hex, hash_hex = stored_hash.split(":")
        salt = bytes.fromhex(salt_hex)
        key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
        return hmac.compare_digest(key.hex(), hash_hex)
    except:
        return False

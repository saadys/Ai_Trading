import secrets
import hashlib
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import HTTPException
from app.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRY = timedelta(hours=1)

def create_access_token(user_id: str, email: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id), "email": email, "type": "access",
        "jti": secrets.token_hex(16), "iat": now, "exp": now + ACCESS_TOKEN_EXPIRY,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=ALGORITHM)

def create_refresh_token(user_id: str) -> tuple[str, str]:
    token_raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token_raw.encode()).hexdigest()
    return token_raw, token_hash

def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Type invalide")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expiré")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token invalide")

def extract_token_from_header(authorization: str | None) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization manquant")
    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Format invalide")
    return parts[1]

def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < 8: return False, "Minimum 8 caractères"
    if not any(c.isupper() for c in password): return False, "Ajoutez majuscule"
    if not any(c.islower() for c in password): return False, "Ajoutez minuscule"
    if not any(c.isdigit() for c in password): return False, "Ajoutez chiffre"
    if not any(c in "!@#$%^&*()_+-=" for c in password): return False, "Ajoutez symbole"
    return True, "Fort"

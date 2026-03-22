import json
import logging
import io
import base64
from datetime import datetime, timedelta, timezone
import pyotp
import qrcode
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.auth.models import *
from app.auth.jwt_handler import create_access_token, create_refresh_token, validate_password_strength
from app.auth.dependencies import get_current_user, rate_limit_login, rate_limit_register, rate_limit_2fa
from app.auth.password import hash_password, verify_password
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger("auth")
REFRESH_TOKEN_EXPIRY = timedelta(days=30)

def _create_session(db, user, refresh_hash, request):
    session = Session(
        user_id=user.id, refresh_token=refresh_hash, is_valid=True,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        expires_at=datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRY,
    )
    db.add(session)
    db.commit()

def _build_response(user, refresh_raw) -> AuthResponse:
    return AuthResponse(
        access_token=create_access_token(str(user.id), user.email),
        refresh_token=refresh_raw, expires_in=3600,
        two_fa_required=not user.two_fa_enabled,
    )

@router.post("/register", response_model=AuthResponse, status_code=201)
async def register(body: RegisterRequest, request: Request, db: Session = Depends(get_db), _: None = Depends(rate_limit_register)):
    is_strong, msg = validate_password_strength(body.password)
    if not is_strong:
        raise HTTPException(status_code=400, detail=msg)
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=409, detail="Email déjà utilisé")
    user = User(email=body.email, password_hash=hash_password(body.password), is_active=True, is_verified=False)
    db.add(user)
    db.flush()
    refresh_raw, refresh_hash = create_refresh_token(str(user.id))
    _create_session(db, user, refresh_hash, request)
    logger.info(json.dumps({"event": "user_registered", "user_id": str(user.id)}))
    return _build_response(user, refresh_raw)

@router.post("/login", response_model=AuthResponse)
async def login(body: LoginRequest, request: Request, db: Session = Depends(get_db), _: None = Depends(rate_limit_login)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé")
    if user.two_fa_enabled:
        if not body.two_fa_code:
            raise HTTPException(status_code=401, detail="Code 2FA requis", headers={"X-2FA-Required": "true"})
        if not pyotp.TOTP(user.two_fa_secret).verify(body.two_fa_code, valid_window=1):
            raise HTTPException(status_code=401, detail="Code 2FA invalide")
    refresh_raw, refresh_hash = create_refresh_token(str(user.id))
    _create_session(db, user, refresh_hash, request)
    logger.info(json.dumps({"event": "user_logged_in", "user_id": str(user.id)}))
    return _build_response(user, refresh_raw)

@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)):
    return UserResponse(id=str(user.id), email=user.email, is_verified=user.is_verified, two_fa_enabled=user.two_fa_enabled, created_at=user.created_at)

@router.post("/2fa/setup", response_model=TwoFASetupResponse)
async def setup_2fa(user: User = Depends(get_current_user), db: Session = Depends(get_db), _: None = Depends(rate_limit_2fa)):
    secret = pyotp.random_base32()
    user.two_fa_secret = secret
    db.commit()
    totp = pyotp.TOTP(secret)
    qr_uri = totp.provisioning_uri(name=user.email, issuer_name="AiTrading")
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(qr_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()
    return TwoFASetupResponse(qr_code_uri=f"data:image/png;base64,{qr_b64}", secret=secret)

@router.post("/2fa/verify")
async def verify_2fa(body: TwoFAVerifyRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db), _: None = Depends(rate_limit_2fa)):
    if not user.two_fa_secret:
        raise HTTPException(status_code=400, detail="Appelez /2fa/setup d'abord")
    if not pyotp.TOTP(user.two_fa_secret).verify(body.code, valid_window=1):
        raise HTTPException(status_code=401, detail="Code invalide")
    user.two_fa_enabled = True
    db.commit()
    return {"message": "2FA activé", "success": True}

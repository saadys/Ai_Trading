import time
import logging
import redis
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.auth.models import User
from app.auth.jwt_handler import extract_token_from_header, decode_access_token
from app.config import settings
from app.database import get_db

logger = logging.getLogger("auth")
redis_client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

async def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    token = extract_token_from_header(request.headers.get("Authorization"))
    payload = decode_access_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide")
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Utilisateur invalide")
    return user

class RateLimiter:
    def __init__(self, max_requests: int, window: int, key_prefix: str = "rl"):
        self.max_requests = max_requests
        self.window = window
        self.key_prefix = key_prefix
    
    async def __call__(self, request: Request) -> None:
        client_ip = request.client.host if request.client else "unknown"
        key = f"{self.key_prefix}:{client_ip}"
        now = time.time()
        try:
            pipe = redis_client.pipeline()
            pipe.zremrangebyscore(key, "-inf", now - self.window)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, self.window)
            results = pipe.execute()
            if results[1] >= self.max_requests:
                raise HTTPException(status_code=429, detail="Trop de requêtes")
        except redis.RedisError:
            logger.warning("Redis indisponible")

rate_limit_login = RateLimiter(5, 300, "rl_login")
rate_limit_register = RateLimiter(3, 600, "rl_register")
rate_limit_2fa = RateLimiter(5, 300, "rl_2fa")

"""
Security-related functions (hashing, tokens, auth)
"""
import base64
import hmac
from datetime import datetime, timedelta
from hashlib import sha256
from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi import status
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from . import config, models
from .database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> models.AdminUser:
    auth_header = request.headers.get(config.TOKEN_HEADER)
    if not auth_header or not auth_header.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    token = auth_header.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        user_id: int = int(payload.get("sub"))
        email: str = payload.get("email")
        if user_id is None or email is None:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = await db.get(models.AdminUser, user_id)
    if not user or user.email != email:
        raise HTTPException(status_code=401, detail="User not found for token")
    return user

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def sign_stream_token(media_id: int, exp_ts: int) -> str:
    msg = f"{media_id}.{exp_ts}".encode()
    sig = hmac.new(config.SECRET_KEY.encode(), msg, sha256).digest()
    return _b64url(sig)

"""
Application Configuration
"""
import os
import secrets
from pathlib import Path

SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
TOKEN_HEADER = "Authorization"
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads")).resolve()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")

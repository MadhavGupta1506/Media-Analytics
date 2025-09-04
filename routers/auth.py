"""
Authentication Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..database import get_db
from ..models import AdminUser
from ..schemas import LoginIn, Token
from ..security import create_access_token, hash_password, verify_password

router = APIRouter()

@router.post("/auth/signup", response_model=Token, status_code=201)
async def signup(payload: schemas.SignupIn, db: AsyncSession = Depends(get_db)):
    existing = (await db.execute(select(AdminUser).where(AdminUser.email == payload.email))).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = AdminUser(email=payload.email, hashed_password=hash_password(payload.password))
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email})
    return Token(access_token=token)

@router.post("/auth/login", response_model=Token)
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)):
    user = (await db.execute(select(AdminUser).where(AdminUser.email == payload.email))).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"sub": str(user.id), "email": user.email})
    return Token(access_token=token)

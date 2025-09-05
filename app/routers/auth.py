from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .. import schemas, models, database, security

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


# -------- SIGNUP --------
@router.post("/signup", response_model=schemas.Token)
async def signup(user: schemas.UserCreate, db: AsyncSession = Depends(database.get_db)):
    # Check if user already exists
    result = await db.execute(select(models.AdminUser).where(models.AdminUser.email == user.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and save
    hashed_pw = security.hash_password(user.password)
    new_user = models.AdminUser(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Generate JWT
    token = security.create_access_token(data={"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}


# -------- LOGIN (Swagger-friendly) --------
@router.post("/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(database.get_db)):
    # form_data.username contains the email
    result = await db.execute(select(models.AdminUser).where(models.AdminUser.email == form_data.username))
    user = result.scalars().first()

    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT
    token = security.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

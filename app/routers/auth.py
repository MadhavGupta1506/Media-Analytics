from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from .. import schemas, models, database, security

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# -------- SIGNUP --------
@router.post("/signup", response_model=schemas.Token)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    # Check if user already exists
    existing_user = db.query(models.AdminUser).filter(models.AdminUser.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password and save
    hashed_pw = security.hash_password(user.password)
    new_user = models.AdminUser(email=user.email, hashed_password=hashed_pw)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT
    token = security.create_access_token(data={"sub": new_user.email})
    return {"access_token": token, "token_type": "bearer"}


# -------- LOGIN (Swagger-friendly) --------
@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    # form_data.username contains the email
    user = db.query(models.AdminUser).filter(models.AdminUser.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT
    token = security.create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

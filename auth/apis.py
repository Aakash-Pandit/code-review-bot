from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.logger import logger
from auth.jwt import JWT_EXPIRE_MINUTES, create_access_token
from auth.passwords import verify_password
from database.db import get_db
from users.models import User

router = APIRouter()


class TokenRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


@router.post("/login", response_model=TokenResponse)
def login(payload: TokenRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        logger.warning("Login failed: user not found", extra={"email": payload.email})
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(payload.password, user.password_hash):
        logger.warning("Login failed: wrong password", extra={"email": payload.email, "user_id": str(user.id)})
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(
        {
            "sub": str(user.id),
            "email": user.email,
        },
        expires_delta=timedelta(minutes=JWT_EXPIRE_MINUTES),
    )
    logger.info("Login successful", extra={"user_id": str(user.id), "email": user.email})
    return TokenResponse(access_token=token, token_type="bearer")

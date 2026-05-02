from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from application.logger import logger
from auth.passwords import hash_password
from database.db import get_db
from users.models import User

router = APIRouter()


class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    email: str
    created_at: str


@router.post("/users", status_code=201, response_model=UserResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        logger.warning("POST /users — email already registered", extra={"email": payload.email})
        raise HTTPException(status_code=409, detail="Email already registered")
    user = User(
        first_name=payload.first_name,
        last_name=payload.last_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(
        "POST /users — signup successful",
        extra={"user_id": str(user.id), "email": user.email, "first_name": user.first_name, "last_name": user.last_name},
    )
    return UserResponse(
        id=str(user.id),
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        created_at=str(user.created_at),
    )

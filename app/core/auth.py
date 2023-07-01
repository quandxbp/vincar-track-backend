from __future__ import annotations

from datetime import datetime, timedelta
from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core import config
from app import config as global_config

from app.schemas.user import *
import app.main as main

global_settings = global_config.get_settings()
USERS_COLLECTION = "users"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
router = APIRouter()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def get_user(
    db: dict[str, dict[str, str]],
    username: Optional[str],
) -> UserInDB | None:
    if username not in db:
        return None
    user_dict = db[username]
    return UserInDB(**user_dict)


async def authenticate_user(username: str, password: str):
    user = await main.app.state.mongo_collections[USERS_COLLECTION].find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> bytes:
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        config.API_SECRET_KEY,
        algorithm=config.API_ALGORITHM,
    )
    return encoded_jwt


# async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
#     credentials_exception = HTTPException(
#         status_code=HTTPStatus.UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#
#     try:
#         payload = jwt.decode(
#             token,
#             config.API_SECRET_KEY,
#             algorithms=[config.API_ALGORITHM],
#         )
#         username = payload.get("sub")
#
#         if username is None:
#             raise credentials_exception
#         token_data = TokenData(username=username)
#
#     except JWTError:
#         raise credentials_exception
#
#     user = get_user(fake_users_db, username=token_data.username)
#
#     if user is None:
#         raise credentials_exception
#     return user


@router.post("/login", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, Any]:
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(
        seconds=config.API_ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    access_token = create_access_token(
        data={"sub": form_data.username},  # type: ignore
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

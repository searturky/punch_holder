from datetime import datetime, timedelta
from typing import Union
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.models.api.token import TokenData
from app.models.api.user import User, UserInDB
from app.models.common import DBCollectionNames
from app.core.config import settings
from jose import JWTError, jwt
from app.models.api.token import oauth2_scheme
from app.utils.common import verify_password


async def get_user(username: str) -> UserInDB:
    doc = await db[DBCollectionNames.USER].find_one({"username": username})
    return UserInDB(**doc) if doc else None


async def authenticate_user(db, username: str, password: str):
    user = await get_user(db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_all_user() -> list[dict]:
    users = await db[DBCollectionNames.USER].find().to_list(None)
    return users


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def create_user(user: UserInDB) -> UserInDB:
    doc = await db[DBCollectionNames.USER].insert_one({
        **user.dict(),
        user.key.bound: True,
    })
    return User(**doc)
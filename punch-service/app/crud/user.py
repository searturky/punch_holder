from datetime import datetime, timedelta
from typing import Union
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.models.api.token import TokenData
from app.models.common import DBCollectionNames
from app.core.config import settings
from jose import JWTError, jwt
from app.models.api.token import oauth2_scheme
from app.utils.common import verify_password
from app.schemas.api.user import User
from app.schemas.api.key import Key
from app.database import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession


async def get_user(username: str) -> User:
    user = await User.find_one_by(username=username)
    return user


async def authenticate_user(username: str, password: str):
    user = await get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
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
    user = await get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def create_user(user: User, key: Key) -> User:
    async with async_session_factory() as session:
        session: AsyncSession
        async with session.begin():
            if key.bound:
                return
            key.bound = True
            session.add(key)
            session.add(user)
            await session.commit()
        await session.refresh(user)

    return user
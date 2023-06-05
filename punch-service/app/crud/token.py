from datetime import datetime, timedelta
from typing import Union
from fastapi import Depends, HTTPException, status
from app.models.api.token import TokenData
from app.models.common import DBCollectionNames
from passlib.context import CryptContext
from app.core.config import settings
from jose import JWTError, jwt
from app.models.api.token import oauth2_scheme


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt
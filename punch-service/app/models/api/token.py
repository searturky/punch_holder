from enum import Enum
from typing import Union
from pydantic import BaseModel, Field
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/token")


class TokenData(BaseModel):
    username: Union[str, None] = None


class Token(BaseModel):
    access_token: str
    token_type: str

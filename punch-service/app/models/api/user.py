from enum import Enum
from typing import Union
from pydantic import BaseModel, Field
from app.schemas.api.key import Key

class CreateUserIn(BaseModel):

    key_code: str
    username: str
    password: str


class UpdateUserIn(BaseModel):

    password: str | None
    email: str | None
    phone: str | None
    nickname: str | None
    user_account: str | None
    session_id: str | None
    login_token: str | None
    

class GetAllUserIn(BaseModel):

    token: str

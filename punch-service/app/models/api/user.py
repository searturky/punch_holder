from enum import Enum
from typing import Union
from pydantic import BaseModel, Field
from app.models.api.key import Key

class CreateUserIn(BaseModel):

    key: str
    username: str
    password: str


class GetAllUserIn(BaseModel):

    token: str


class User(BaseModel):

    key: Key
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: bool = False
    phone: str = None
    nickname: str = None
    user_account: str = None
    session_id: str = None
    login_token: str = None

    # @property
    # def display_name(self) -> str:
    #     return self.username

    # @property
    # def is_authenticated(self) -> bool:
    #     return True

    # @property
    # def username(self) -> str:
    #     return self.nickname or self.user_account or self.token

    # @property
    # def is_admin(self) -> bool:
    #     return self.token_type == TokenTypes.ADMIN or self.token_type == TokenTypes.SUPERUSER
    
    # @property
    # def is_superuser(self) -> bool:
    #     return self.token_type == TokenTypes.SUPERUSER


class UserInDB(User):
    hashed_password: str
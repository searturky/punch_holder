from enum import Enum
from bson import ObjectId
from pydantic import BaseModel, Field
from app.models.extra import JsonObjectID


class TokenTypes(str, Enum):

    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class UserIn(BaseModel):

    token: str
    user_account: str = None
    session_id: str = None
    login_token: str = None


class GetAllUserIn(BaseModel):

    token: str


class User(BaseModel):

    id: JsonObjectID = Field(default_factory=JsonObjectID, alias="_id")
    token: str
    token_type: TokenTypes
    nickname: str = None
    user_account: str = None
    session_id: str = None
    login_token: str = None

    class Config:
        json_encoders = {ObjectId: str}

    @property
    def display_name(self) -> str:
        return self.username

    @property
    def is_authenticated(self) -> bool:
        return True

    @property
    def username(self) -> str:
        return self.nickname or self.user_account or self.token

    @property
    def is_admin(self) -> bool:
        return self.token_type == TokenTypes.ADMIN or self.token_type == TokenTypes.SUPERUSER
    
    @property
    def is_superuser(self) -> bool:
        return self.token_type == TokenTypes.SUPERUSER
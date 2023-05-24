from enum import Enum
from bson import ObjectId
from pydantic import BaseModel, Field
from app.models.extra import JsonObjectID


class KeyTypes(str, Enum):

    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class Key(BaseModel):

    id: JsonObjectID = Field(default_factory=JsonObjectID, alias="_id")
    key: str
    key_type: KeyTypes
    bound: bool = False

    class Config:
        json_encoders = {ObjectId: str}

    @property
    def is_admin_key(self) -> bool:
        return self.token_type == KeyTypes.ADMIN or self.token_type == KeyTypes.SUPERUSER
    
    @property
    def is_superuser_key(self) -> bool:
        return self.token_type == KeyTypes.SUPERUSER
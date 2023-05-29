from enum import Enum
from pydantic import BaseModel, Field


class KeyTypes(str, Enum):

    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class Key(BaseModel):

    code: str
    key_type: KeyTypes
    bound: bool = False

    @property
    def is_admin_key(self) -> bool:
        return self.key_type == KeyTypes.ADMIN or self.key_type == KeyTypes.SUPERUSER
    
    @property
    def is_superuser_key(self) -> bool:
        return self.key_type == KeyTypes.SUPERUSER
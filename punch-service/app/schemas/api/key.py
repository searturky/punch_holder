import enum
from app.schemas.common import CommonBase
from sqlalchemy import Column, Boolean, String, Enum


class KeyTypes(str, enum.Enum):

    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class Key(CommonBase):

    __tablename__ = "key"
    code = Column(String)
    key_type = Column(Enum(KeyTypes))
    bound = Column(Boolean, default=False)
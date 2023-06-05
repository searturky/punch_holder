import enum
from app.schemas.api.user import User
from app.schemas.common import CommonBase
from sqlalchemy import Column, Boolean, String, Enum
from sqlalchemy.orm import relationship, Mapped


class KeyTypes(str, enum.Enum):

    USER = "user"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class Key(CommonBase):

    __tablename__ = "key"

    code: Mapped[str] = Column(String(256))
    key_type: Mapped[KeyTypes] = Column(Enum(KeyTypes))
    bound: Mapped[bool] = Column(Boolean, default=False)

    user: Mapped["User"] = relationship()

    @property
    def is_admin_key(self) -> bool:
        return self.key_type == KeyTypes.ADMIN or self.key_type == KeyTypes.SUPERUSER
    
    @property
    def is_superuser_key(self) -> bool:
        return self.key_type == KeyTypes.SUPERUSER
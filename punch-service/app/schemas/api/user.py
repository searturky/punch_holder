import enum
from typing import Any, List
from app.schemas.api.task import PunchTask, TestTask
from app.schemas.common import CommonBase
from sqlalchemy import Column, Boolean, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column


class User(CommonBase):

    __tablename__ = "user"
    
    key_id = mapped_column(Integer, ForeignKey("key.id"))
    username: Mapped[str] = Column(String(32))
    password: Mapped[str] = Column(String(256))
    disabled: Mapped[bool] = Column(Boolean, default=False)
    email: Mapped[str] = Column(String(64))
    phone: Mapped[str] = Column(String(32))
    nickname: Mapped[str] = Column(String(32))

    punch_tasks: Mapped[List["PunchTask"]] = relationship()
    test_tasks: Mapped[List["TestTask"]] = relationship()

    # punch login info 
    user_account: Mapped[str] = Column(String(256))
    session_id: Mapped[str] = Column(String(256))
    login_token: Mapped[str] = Column(String(256))

    # key: Key
    # username: str
    # email: Union[str, None] = None
    # full_name: Union[str, None] = None
    # disabled: bool = False
    # phone: str = None
    # nickname: str = None
    # user_account: str = None
    # session_id: str = None
    # login_token: str = None

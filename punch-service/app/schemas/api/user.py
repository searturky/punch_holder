import enum
from typing import Any, List, TYPE_CHECKING
from app.schemas.api.task import PunchTask, TestTask, TaskType
from app.schemas.common import CommonBase
from sqlalchemy import Column, Boolean, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.schemas.api.key import Key, KeyTypes


if TYPE_CHECKING:
    from app.schemas.api.task import TaskBase


class User(CommonBase):

    __tablename__ = "user"
    
    key: Mapped["Key"] = relationship("Key", back_populates="user", lazy=False)
    key_id: Mapped[int] = mapped_column(Integer, ForeignKey("key.id"))
    username: Mapped[str] = Column(String(32))
    password: Mapped[str] = Column(String(256))
    disabled: Mapped[bool] = Column(Boolean, default=False)
    email: Mapped[str] = Column(String(64))
    phone: Mapped[str] = Column(String(32))
    nickname: Mapped[str] = Column(String(32))

    punch_tasks: Mapped[List["PunchTask"]] = relationship(back_populates="user")
    test_tasks: Mapped[List["TestTask"]] = relationship(back_populates="user")

    # punch login info 
    user_account: Mapped[str] = Column(String(256))
    session_id: Mapped[str] = Column(String(256))
    login_token: Mapped[str] = Column(String(256))

    @property
    def is_admin(self) -> bool:
        return self.key.key_type == KeyTypes.ADMIN or self.key.key_type == KeyTypes.SUPERUSER

    @property
    def is_superuser(self) -> bool:
        return self.key.key_type == KeyTypes.SUPERUSER

    async def get_tasks_by_type(self, task_type: "TaskType") -> List["TaskBase"]:
        if task_type == TaskType.PUNCH:
            return await self.awaitable_attrs.punch_tasks
        elif task_type == TaskType.TEST:
            return await self.awaitable_attrs.test_tasks
        

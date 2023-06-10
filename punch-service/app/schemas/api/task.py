import enum
import pprint 
from httpx import AsyncClient, Response
from uuid import uuid1
from random import randint
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from app.schemas.common import CommonBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import relationship, Mapped, mapped_column
from apscheduler.triggers.cron import CronTrigger
from app.models.holder.holder_api import TodayStaticId, TodayPunchInfo
from app.http_client import get_http_client
from typing import TYPE_CHECKING
from datetime import datetime


if TYPE_CHECKING:
    from app.schemas.api.user import User


class TaskStatus(str, enum.Enum):

    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"


class TaskType(str, enum.Enum):
    
    PUNCH = "punch"
    TEST = "test"


class TaskBase(CommonBase):

    __abstract__ = True
 
    job_id: Mapped[str] = Column(String(64), default=uuid1().hex, comment="任务id")
    job_name: Mapped[str] = Column(String(255), comment="任务名称")
    description: Mapped[str] = Column(String(255), comment="任务描述")
    status: Mapped[TaskStatus] = Column(Enum(TaskStatus), default=TaskStatus.IDLE, comment="任务状态")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))

    async def start(self, scheduler: AsyncIOScheduler, trigger: CronTrigger=None):
        self.status = TaskStatus.PENDING
        await self.save()
        try:
            # await self._run()
            scheduler.add_job(
                func=self._run, 
                trigger=trigger or CronTrigger(day="*", hour="8,18", minute=f"{randint(45, 59)}", second=f"{randint(0, 59)}"), 
                replace_existing=True,
                id=self.job_id,
                name=self.job_name,
            )
        except Exception as e:
            self.status = TaskStatus.FAILED
            await self.save()
            raise e
    
    async def _run(self):
        try:
            self.status = TaskStatus.RUNNING
            await self.save()
            await self.run()
            self.status = TaskStatus.FINISHED
            await self.save()
        except Exception as e:
            self.status = TaskStatus.FAILED
            await self.save()
            raise e

    async def run(self):
        raise NotImplementedError


class PunchTask(TaskBase):

    __tablename__ = "punch_task"

    type: Mapped[TaskType] = Column(Enum(TaskType), comment="任务类型", default=TaskType.PUNCH, nullable=False)

    user_account = Column(String(64), nullable=False, comment="用户在holder的账号")
    session_id = Column(String(64), nullable=False, comment="用户在holder的session_id")
    login_token = Column(String(256), nullable=False, comment="用户登录holder的token")
    
    user: Mapped["User"] = relationship(back_populates="punch_tasks")

    def is_valid_start_arg(self):
        if not self.user_account:
            return False
        if not self.session_id:
            return False
        if not self.login_token:
            return False
        return True

    async def run(self):
        punch_info: TodayPunchInfo = await TodayStaticId.request(
            user_account=self.user_account,
            session_id=self.session_id,
            login_token=self.login_token,
        )
        print('=================发起请求==========================', datetime.now())
        print('=================今天是否休息==========================',punch_info.is_rest)
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(punch_info.res_json)
        if punch_info.is_rest:
            return
        ...

class TestTask(TaskBase):

    __tablename__ = "test_task"

    type: Mapped[TaskType] = Column(Enum(TaskType), comment="任务类型", default=TaskType.TEST, nullable=False)

    test_msg = Column(String(255), nullable=False, comment="测试信息")
    user: Mapped["User"] = relationship(back_populates="test_tasks")

    async def run(self):
        print(f"test task {self.id} is running")

    

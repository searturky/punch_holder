
import enum 
from uuid import uuid4
from random import randint
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from app.schemas.common import CommonBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import relationship, Mapped, mapped_column
from apscheduler.triggers.cron import CronTrigger
from app.models.holder.holder_api import TodayStaticId, TodayPunchInfo
from app.http_client import get_http_client


class TaskStatus(str, enum.Enum):

    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"


class TaskBase(CommonBase):

    __abstract__ = True
 
    job_id: Mapped[str] = Column(String(32), default=uuid4().hex, comment="任务id")
    job_name: Mapped[str] = Column(String(255), comment="任务名称")
    description: Mapped[str] = Column(String(255), comment="任务描述")
    status: Mapped[TaskStatus] = Column(Enum(TaskStatus), default=TaskStatus.IDLE, comment="任务状态")
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"))


class PunchTask(TaskBase):

    __tablename__ = "punch_task"

    user_account = Column(String(32), nullable=False, comment="用户在holder的账号")
    session_id = Column(String(32), nullable=False, comment="用户在holder的session_id")
    login_token = Column(String(32), nullable=False, comment="用户登录holder的token")

    async def start(self, scheduler: AsyncIOScheduler):
        self.status = TaskStatus.PENDING
        await self.save()
        try:
            scheduler.add_job(
                func=self.run, 
                trigger = CronTrigger(day="*", hour="8,18", minute=f"{randint(45, 59)}", second=f"{randint(0, 59)}"), 
                replace_existing=True,
                id=self.job_id,
                name=self.job_name,
            )
            ...
        except Exception as e:
            self.status = TaskStatus.FAILED
            await self.save()
            raise e

    async def run(self):
        self.status = TaskStatus.RUNNING
        await self.save()
        punch_info: TodayPunchInfo = TodayStaticId.request(
            user_account=self.user_account,
            session_id=self.session_id,
            login_token=self.login_token,
        )
        self.status = TaskStatus.FINISHED
        await self.save()

class TestTask(TaskBase):

    __tablename__ = "test_task"

    test_msg = Column(String(255), nullable=False, comment="测试信息")

    async def start(self, scheduler: AsyncIOScheduler):
        self.status = TaskStatus.PENDING
        await self.save()
        try:
            r1 = scheduler.add_job(
                func=self.run, 
                trigger = CronTrigger(day="*", hour="8,18", minute=f"{randint(45, 58)}", second=f"{randint(0, 59)}"), 
                replace_existing=True, 
                id=self.job_id,
                name=self.job_name,
            )
            ...
        except Exception as e:
            self.status = TaskStatus.FAILED
            await self.save()
            raise e

    async def run(self):
        self.status = TaskStatus.RUNNING
        await self.save()
        print(f"test task {self.id} is running")
        self.status = TaskStatus.FINISHED
        await self.save()

    

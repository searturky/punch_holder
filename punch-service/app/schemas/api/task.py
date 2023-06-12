import asyncio
import enum
import logging
from httpx import AsyncClient, Response
from uuid import uuid1
from random import randint
from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from app.schemas.common import CommonBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import relationship, Mapped, mapped_column
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from app.models.holder.holder_api import AfternoonInfo, MorningInfo, PunchIn, TodayStaticId, TodayPunchInfo
from typing import TYPE_CHECKING
from app.utils.time_util import local_now
from datetime import datetime, timedelta,timezone


logger = logging.getLogger("uvicorn")
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
            scheduler.add_job(
                func=self._run,
                trigger=DateTrigger(run_date=datetime.now()),
            )
            scheduler.add_job(
                func=self._run, 
                trigger=trigger or CronTrigger(day="*", hour="8,18", minute="45", second="0"), 
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

    user_account: Mapped[str] = Column(String(64), nullable=False, comment="用户在holder的账号")
    session_id: Mapped[str] = Column(String(64), nullable=False, comment="用户在holder的session_id")
    login_token: Mapped[str] = Column(String(256), nullable=False, comment="用户登录holder的token")
    
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
        await asyncio.sleep(randint(0, 60 * 12))
        punch_info: TodayPunchInfo = await TodayStaticId.request(
            user_account=self.user_account,
            session_id=self.session_id,
            login_token=self.login_token,
        )
        logger.info(f'=================发起请求=========================={local_now()}')
        logger.info(f'=================今天是否休息=========================={punch_info.is_rest}')
        logger.info(f'{punch_info.res_json}')
        if punch_info.is_rest:
            return
        should_punch, punch_type, card_ponit = await PunchIn.should_punch_in(punch_info)
        if not PunchIn.should_punch_in(punch_info):
            return
        static_id = punch_info.static_id
        logger.info(f'=================punch_type=========================={punch_type}')
        logger.info(f'=================card_ponit=========================={card_ponit}')
        logger.info(f'=================should_punch=========================={should_punch}')
        logger.info('=================开始打卡==========================')
        # r = await PunchIn.request(
        #     login_token=self.login_token,
        #     user_account=self.user_account,
        #     punch_type=punch_type,
        #     static_id=static_id,
        #     session_id=self.session_id,
        #     card_point=card_ponit,
        # )
        return 

class TestTask(TaskBase):

    __tablename__ = "test_task"

    type: Mapped[TaskType] = Column(Enum(TaskType), comment="任务类型", default=TaskType.TEST, nullable=False)

    test_msg = Column(String(255), nullable=False, comment="测试信息")
    user: Mapped["User"] = relationship(back_populates="test_tasks")

    async def run(self):
        print(f"test task {self.id} is running")

    

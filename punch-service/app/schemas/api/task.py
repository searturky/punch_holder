import re
import time
import jwt
import enum
import asyncio
import logging
from httpx import AsyncClient, Response, Headers
from uuid import uuid1
from random import randint
from app.utils.time_util import tzinfo
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, text
from app.schemas.common import CommonBase
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import relationship, Mapped, mapped_column
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.combining import OrTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.holder.holder_api import AfternoonInfo, PunchDCJWT, PunchIn, TodayStaticId, TodayPunchInfo, PunchDCIn
from typing import TYPE_CHECKING, Literal
from app.utils.time_util import local_now
from datetime import datetime, timedelta,timezone
if TYPE_CHECKING:
    from app.schemas.api.user import User


logger = logging.getLogger("uvicorn")


class TaskStatus(str, enum.Enum):

    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    FINISHED = "finished"
    FAILED = "failed"


class TaskType(str, enum.Enum):
    
    PUNCH = "punch"
    TEST = "test"

    def get_task_class(self) -> "TaskBase":
        if self == TaskType.PUNCH:
            return PunchTask
        elif self == TaskType.TEST:
            return TestTask
        return None
    

class PunchTimeType(int, enum.Enum):
    
    MORNING = 0
    AFTERNOON = 1


class TaskBase(CommonBase):

    __abstract__ = True
 
    job_id: Mapped[str] = Column(String(64), default=lambda x: uuid1().hex, comment="任务id")
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
                trigger=trigger or CronTrigger(day="*", hour="8,18", minute="31", second="0", timezone=tzinfo), 
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
    
    async def do_update_user_info(self):
        async with self._async_session_factory() as session:
            session: "AsyncSession"
            async with session.begin():
                session.add(self)
                self.user.login_token = self.login_token
                self.user.session_id = self.session_id
                self.user.user_account = self.user_account

    async def do_update_user_info_at_once(self):
        async with self._async_session_factory() as session:
            session: "AsyncSession"
            async with session.begin():
                stmt = text("""
                    update 
                        "user"
                    set
                        login_token=:login_token, 
                        session_id=:session_id, 
                        user_account=:user_account 
                    where 
                        id=:user_id
                """)
                await session.execute(stmt, {
                    "login_token": self.login_token,
                    "session_id": self.session_id,
                    "user_account": self.user_account,
                    "user_id": self.user_id,
                })

    async def ensure_latest_user_info(self):
        async with self._async_session_factory() as session:
            async with session.begin():
                session: "AsyncSession"
                session.add(self)
                task_update_time = await self.awaitable_attrs.update_at
                user_obj = await self.awaitable_attrs.user
                user_update_time = await user_obj.awaitable_attrs.update_at
                if task_update_time > user_update_time:
                    return
                self.user_account = self.user.user_account
                self.session_id = self.user.session_id
                self.login_token = self.user.login_token
    
    async def update_user_info(self, headers: Headers):
        for k, v in headers.items():
            if k == "set-cookie":
                if match := re.search(r"session_id=(.*?);", v):
                    session_id = match.group(1)
                    self.session_id = session_id
            if k == "loginToken":
                self.login_token = v

        await self.do_update_user_info()

    async def update_user_info_at_once(self, headers: Headers):
        for k, v in headers.items():
            if k == "set-cookie":
                if match := re.search(r"session_id=(.*?);", v):
                    session_id = match.group(1)
                    self.session_id = session_id
            if k == "loginToken":
                self.login_token = v

        await self.do_update_user_info_at_once()

    async def punch_morning(self):
        logger.info(f'\n\n======================Task Starting Running======================={local_now()}')
        punch_info, punch_info_res = await TodayStaticId.request(
            user_account=self.user_account,
            session_id=self.session_id,
            login_token=self.login_token,
        )
        await self.update_user_info_at_once(punch_info_res.headers)
        logger.info(f'================= >>>>>> Request For Get Today Punch Info==========================     {local_now()}')
        logger.info(f'=================Today Is Rest==========================    {punch_info.is_rest}')
        logger.info(f'{punch_info.res_json}')
        should_punch, punch_type, card_ponit = PunchIn.should_punch_in(punch_info)
        logger.info(f'=================should_punch==========================  {should_punch}')
        logger.info(f'=================punch_type==========================   {punch_type}')
        logger.info(f'=================card_ponit==========================  {card_ponit}')
        if not should_punch:
            logger.info('======================No Need To Punch==========================')
            logger.info('======================End==========================')
            return
        static_id = punch_info.static_id
        logger.info('================= >>>>>> Request For Punch==========================')
        res: Response = await PunchIn.request(
            login_token=self.login_token,
            user_account=self.user_account,
            punch_type=punch_type,
            static_id=static_id,
            session_id=self.session_id,
            card_point=card_ponit,
        )
        await self.update_user_info_at_once(res.headers)
        logger.info('====================Success==========================')
        logger.info('======================End==========================\n')

    async def run_once(self):
        logger.info(f'\n\n======================Task Starting Running======================={local_now()}')
        punch_info, punch_info_res = await TodayStaticId.request(
            user_account=self.user_account,
            session_id=self.session_id,
            login_token=self.login_token,
        )
        await self.update_user_info_at_once(punch_info_res.headers)
        logger.info(f'================= >>>>>> Request For Get Today Punch Info==========================     {local_now()}')
        logger.info(f'=================Today Is Rest==========================    {punch_info.is_rest}')
        logger.info(f'{punch_info.res_json}')
        if punch_info.is_rest:
            logger.info('======================End==========================')
            return
        should_punch, punch_type, card_ponit = PunchIn.should_punch_in(punch_info)
        logger.info(f'=================should_punch==========================  {should_punch}')
        logger.info(f'=================punch_type==========================   {punch_type}')
        logger.info(f'=================card_ponit==========================  {card_ponit}')
        if not should_punch:
            logger.info('======================No Need To Punch==========================')
            logger.info('======================End==========================')
            return
        static_id = punch_info.static_id
        logger.info('================= >>>>>> Request For Punch==========================')
        res: Response = await PunchIn.request(
            login_token=self.login_token,
            user_account=self.user_account,
            punch_type=punch_type,
            static_id=static_id,
            session_id=self.session_id,
            card_point=card_ponit,
        )
        await self.update_user_info_at_once(res.headers)
        logger.info('====================Success==========================')
        logger.info('======================End==========================\n')

    async def run(self, call_immediately: bool = False):
        logger.info(f'\n\n======================Task Starting Running======================={local_now()}')
        if not call_immediately:
            sleep_time = randint(0, 60 * 12)
            logger.info(f'======================Sleeping {sleep_time} Second=======================')
            await asyncio.sleep(sleep_time)
        await self.ensure_latest_user_info()
        punch_info, punch_info_res = await TodayStaticId.request(
            user_account=self.user_account,
            session_id=self.session_id,
            login_token=self.login_token,
        )
        await self.update_user_info(punch_info_res.headers)
        logger.info(f'================= >>>>>> Request For Get Today Punch Info==========================     {local_now()}')
        logger.info(f'=================Today Is Rest==========================    {punch_info.is_rest}')
        logger.info(f'{punch_info.res_json}')
        if punch_info.is_rest:
            logger.info('======================End==========================')
            return
        should_punch, punch_type, card_ponit = PunchIn.should_punch_in(punch_info)
        logger.info(f'=================should_punch==========================  {should_punch}')
        logger.info(f'=================punch_type==========================   {punch_type}')
        logger.info(f'=================card_ponit==========================  {card_ponit}')
        if not should_punch:
            logger.info('======================No Need To Punch==========================')
            logger.info('======================End==========================')
            return
        static_id = punch_info.static_id
        logger.info('================= >>>>>> Request For Punch==========================')
        res: Response = await PunchIn.request(
            login_token=self.login_token,
            user_account=self.user_account,
            punch_type=punch_type,
            static_id=static_id,
            session_id=self.session_id,
            card_point=card_ponit,
        )
        await self.update_user_info(res.headers)
        logger.info('====================Success==========================')
        logger.info('======================End==========================\n')
    

class TestTask(TaskBase):

    __tablename__ = "test_task"

    type: Mapped[TaskType] = Column(Enum(TaskType), comment="任务类型", default=TaskType.TEST, nullable=False)

    test_msg = Column(String(255), nullable=False, comment="测试信息")
    user: Mapped["User"] = relationship(back_populates="test_tasks")

    async def run(self):
        print(f"test task {self.id} is running")

    
class PunchDCTask(TaskBase):

    __tablename__ = "punch_task_dc"

    type: Mapped[TaskType] = Column(Enum(TaskType), comment="任务类型", default=TaskType.PUNCH, nullable=False)

    token: Mapped[str] = Column(String(256), nullable=False, comment="打卡请求头里的Authorization")
    
    user: Mapped["User"] = relationship(back_populates="punch_dc_tasks")

    async def start(self, scheduler: AsyncIOScheduler, trigger: CronTrigger=None):
        self.status = TaskStatus.PENDING
        await self.save()
        default_trigger = OrTrigger([
            CronTrigger(day="*", hour="8", minute="45", second="0", timezone=tzinfo),
            CronTrigger(day="*", hour="18", minute="10", second="0", timezone=tzinfo)
        ])
        try:
            scheduler.add_job(
                func=self._run, 
                trigger=trigger or default_trigger, 
                replace_existing=True,
                id=self.job_id,
                name=self.job_name,
            )
        except Exception as e:
            self.status = TaskStatus.FAILED
            await self.save()
            raise e

    async def run_once(self, punch_time_type: PunchTimeType):
        logger.info(f'\n\n======================Task Punch DC Starting Running======================={local_now()}')
        logger.info('================= >>>>>> Request For Punch==========================')
        res: Response = await PunchDCIn.request(
            authorization=self.token,
            clockin_type=punch_time_type,
        )
        logger.info('====================Success==========================')
        logger.info('======================End==========================\n')

    @staticmethod
    async def get_jwt():
        res = await PunchDCJWT.request()
        body: dict = res.json()
        data = body.get("Data") or {}
        token = data.get("WxToken") or {}
        if not token:
            logger.info('======================Get New Token Failed==========================')
            raise Exception("Get New Token Failed")
        return 'bearer ' + token
    
    async def ensure_latest_user_info(self):
        async with self._async_session_factory() as session:
            async with session.begin():
                session: "AsyncSession"
                session.add(self)
                token = self.token[7:]
                decoded: dict = jwt.decode(token, options={"verify_signature": False})
                exp = decoded.get("exp")
                if not exp or exp < int(time.time()):
                    logger.info('======================Token Expired==========================')
                    logger.info('======================Request New Token==========================')
                    self.token = await self.get_jwt()
                session.commit()
                session.refresh(self)

    async def run(self, call_immediately: bool = False):
        logger.info(f'\n\n======================Task Starting Running======================={local_now()}')
        if not call_immediately:
            sleep_time = randint(0, 60 * 14)
            logger.info(f'======================Sleeping {sleep_time} Second=======================')
            await asyncio.sleep(sleep_time)
        await self.ensure_latest_user_info()
        punch_info, punch_info_res = await TodayStaticId.request(
            user_account=self.user_account,
            session_id=self.session_id,
            login_token=self.login_token,
        )
        await self.update_user_info(punch_info_res.headers)
        logger.info(f'================= >>>>>> Request For Get Today Punch Info==========================     {local_now()}')
        logger.info(f'=================Today Is Rest==========================    {punch_info.is_rest}')
        logger.info(f'{punch_info.res_json}')
        if punch_info.is_rest:
            logger.info('======================End==========================')
            return
        should_punch, punch_type, card_ponit = PunchIn.should_punch_in(punch_info)
        logger.info(f'=================should_punch==========================  {should_punch}')
        logger.info(f'=================punch_type==========================   {punch_type}')
        logger.info(f'=================card_ponit==========================  {card_ponit}')
        if not should_punch:
            logger.info('======================No Need To Punch==========================')
            logger.info('======================End==========================')
            return
        static_id = punch_info.static_id
        logger.info('================= >>>>>> Request For Punch==========================')
        res: Response = await PunchIn.request(
            login_token=self.login_token,
            user_account=self.user_account,
            punch_type=punch_type,
            static_id=static_id,
            session_id=self.session_id,
            card_point=card_ponit,
        )
        await self.update_user_info(res.headers)
        logger.info('====================Success==========================')
        logger.info('======================End==========================\n')
from enum import Enum
from typing import List, Literal
from pydantic import BaseModel, Field
from app.schemas.api.task import TaskType, PunchTimeType

class GetAllTaskIn(BaseModel):

    type: List["TaskType"] = Field([], description="任务类型")


class RegisterPunchTaskIn(BaseModel):

    user_account: str | None = Field(None, description="打卡账号")
    session_id: str | None = Field(None, description="打卡session_id")
    login_token: str | None = Field(None, description="打卡login_token")
    job_name: str | None = Field(None, description="打卡任务别名")


class RunPunchDCTaskIn(BaseModel):

    jwt: str | None = Field(description="打卡jwt")
    punch_type: "PunchTimeType" = Field(description="打卡类型, 0 为早上打卡，1 为下午打卡")


class RegisterTestTaskIn(BaseModel):

    test_msg: str = Field(..., description="测试消息")


class CallPunchTaskIn(BaseModel):
    user_account: str | None = Field(None, description="打卡账号")
    session_id: str | None = Field(None, description="打卡session_id")
    login_token: str | None = Field(None, description="打卡login_token")



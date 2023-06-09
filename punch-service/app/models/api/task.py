from enum import Enum
from typing import List
from pydantic import BaseModel, Field
from app.schemas.api.task import TaskType

class GetAllTaskIn(BaseModel):

    type: List["TaskType"] = Field([], description="任务类型")


class RegisterPunchTaskIn(BaseModel):

    user_account: str | None = Field(None, description="打卡账号")
    session_id: str | None = Field(None, description="打卡session_id")
    login_token: str | None = Field(None, description="打卡login_token")
    job_name: str | None = Field(None, description="打卡任务别名")


class RegisterTestTaskIn(BaseModel):

    test_msg: str = Field(..., description="测试消息")




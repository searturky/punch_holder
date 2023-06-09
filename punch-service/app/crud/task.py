from typing import List
from app.schemas.api.user import User
from app.database import async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.api.task import PunchTask, TestTask, TaskBase, TaskType


async def get_tasks_from_current_user(user: "User", task_type: "TaskType") -> List["TaskBase"]:
    async with async_session_factory() as session:
        session: AsyncSession
        session.add(user)
        tasks = await user.get_tasks_by_type(task_type)
        return tasks
    

async def get_all_user_tasks(task_type: "TaskType") -> List["TaskBase"]:
    if task_type == TaskType.PUNCH:
        return await PunchTask.find_all()
    elif task_type == TaskType.TEST:
        return await TestTask.find_all()
    return []
import jwt
import time
import base64
from typing import List, TYPE_CHECKING, Literal, cast
from app.crud.user import get_current_active_user, get_current_active_admin_user
from app.crud.task import get_tasks_from_current_user, get_all_user_tasks
from fastapi import APIRouter, Body, Depends, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from app.models.api.task import CallPunchTaskIn, RegisterPunchTaskIn, RegisterTestTaskIn, RunPunchDCTaskIn, RunPunchJWtDCTaskIn
from app.schemas.api.task import TestTask, PunchTask, TaskBase, TaskType, TaskStatus, PunchDCTask
from app.schemas.api.user import User
from app.scheduler import scheduler
from fastapi.encoders import jsonable_encoder
if TYPE_CHECKING:
    from apscheduler.job import Job

router = APIRouter()
router.tags = ["任务"]


@router.get("", description="查询当前用户所有任务", summary="查询当前用户所有任务")
async def get_user_all_task(select_type: List[TaskType] = Query([]), user: User = Depends(get_current_active_user)):
    tasks: List["TaskBase"] = []
    if not select_type:
        select_type = [t for t in TaskType]
    for type in select_type:
        tasks.extend(await get_tasks_from_current_user(user, type))
    return JSONResponse(status_code=status.HTTP_200_OK, content={"tasks": jsonable_encoder([task.to_dict() for task in tasks])})


@router.get("/all", description="查询所有任务", summary="查询所有任务")
async def get_all_task(select_type: List[TaskType] = Query([]), user: User = Depends(get_current_active_admin_user)):
    tasks: List["TaskBase"] = []
    if not select_type:
        select_type = [type for type in TaskType]
    for type in select_type:
        tasks.extend(await get_all_user_tasks(type))
    return JSONResponse(status_code=status.HTTP_200_OK, content={"tasks": jsonable_encoder([task.to_dict() for task in tasks])})


@router.post("/punch", description="注册一个新打卡任务", summary="注册一个新打卡任务")
async def register_punch_task(punch_task_info: RegisterPunchTaskIn = Body(...), user: User = Depends(get_current_active_user)):
    punch_task: PunchTask = PunchTask(**{
        "session_id": user.session_id,
        "user_account": user.user_account,
        "login_token": user.login_token,
        **punch_task_info.dict(exclude_unset=True),
        "user_id": user.id
    })
    if not punch_task.is_valid_start_arg():
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "打卡任务注册失败，参数不合法"})
    await punch_task.save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "打卡任务注册成功"})

@router.post("/punch/dc", description="注册一个新打卡任务（dc）", summary="注册一个新打卡任务（dc）")
async def register_punch_task(user: User = Depends(get_current_active_user)):
    token = await PunchDCTask.get_jwt()
    punch_task: PunchDCTask = PunchDCTask(token=token)
    await punch_task.save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "打卡任务注册成功"})

@router.post("/register/dc/jwt", description="注册DC的jwt", summary="注册DC的jwt")
async def register_dc_jwt(req_jwt: str = Body(...), user: User = Depends(get_current_active_user)):
    if not req_jwt:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "jwt不能为空"})
    if not req_jwt.startswith("bearer ") and not req_jwt.startswith("Bearer "):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "jwt格式不合法"})
    info_token = req_jwt[7:]
    decoded: dict = jwt.decode(info_token, options={"verify_signature": False})
    exp = decoded.get("exp")
    if not exp:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "jwt不合法"})
    if exp < int(time.time()):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "jwt已过期"})
    user.dc_jwt = req_jwt
    await user.save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "注册jwt成功"})

@router.post("/punch/once/dc/jwt", description="马上打卡jwt", summary="马上打卡jwt")
async def run_punch_task_dc_jwt(punch_task_info: RunPunchJWtDCTaskIn = Body(...), user: User = Depends(get_current_active_user)):
    token = user.dc_jwt
    if not token:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "jwt不能为空"})
    punch_task: PunchDCTask = PunchDCTask(token=token)
    await punch_task.run_once(punch_task_info.punch_type)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "打卡成功"})

@router.post("/punch/once/dc", description="马上打卡（dc）", summary="马上打卡（dc）")
async def register_punch_task_dc(punch_task_info: RunPunchDCTaskIn = Body(...), user: User = Depends(get_current_active_user)):
    token = punch_task_info.jwt
    if not token:
        token = await PunchDCTask.get_jwt()
    if token.startswith("bearer ") or token.startswith("Bearer "):
        info_token = token[7:]
    decoded: dict = jwt.decode(info_token, options={"verify_signature": False})
    exp = decoded.get("exp")
    if not exp:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "jwt不合法"})
    if exp < int(time.time()):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "jwt已过期"})
    punch_task = PunchDCTask(token=token)
    await punch_task.run_once(punch_task_info.punch_type)
    # if not punch_task.is_valid_start_arg():
    #     return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "打卡任务注册失败，参数不合法"})
    # await punch_task.save()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "打卡成功"})

@router.get("/punch/once/dc/3REffw3/{punch_type}", description="马上打卡（dc）", summary="马上打卡（dc）")
async def register_punch_task_dc_get(punch_type: Literal["0", "1"]):
    token: str = await PunchDCTask.get_jwt()
    if token.startswith("bearer ") or token.startswith("Bearer "):
        info_token = token[7:]
    decoded: dict = jwt.decode(info_token, options={"verify_signature": False})
    exp = decoded.get("exp")
    if not exp:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "jwt不合法"})
    if exp < int(time.time()):
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "jwt已过期"})
    punch_task = PunchDCTask(token=token)
    await punch_task.run_once(int(punch_type))
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "打卡成功"})

@router.get("/punch/start/{task_id}", description="通过id开始一个打卡任务", summary="通过id开始一个打卡任务")
async def start_punch_task_by_id(task_id: int, user: User = Depends(get_current_active_user)):
    task: TaskBase = await TaskBase.find_by_id(task_id)
    if not task:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "该打卡任务不存在"})
    if task.status != TaskStatus.IDLE and task.status != TaskStatus.FAILED:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": "打卡任务已经在运行中"})
    await task.start(scheduler)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "打卡任务开始成功"})


@router.post("/test", description="注册一个新测试任务", summary="注册一个新测试任务")
async def register_test_task(test_task_info: RegisterTestTaskIn = Body(...), user: User = Depends(get_current_active_user)):
    test_task = TestTask(**test_task_info.dict(), user_id=user.id)
    await test_task.save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "测试任务注册成功"})


@router.get("/test/start/{task_id}", description="通过id开始一个测试任务", summary="通过id开始一个测试任务")
async def start_test_task_by_id(task_id: int, user: "User" = Depends(get_current_active_user)):
    test_task: TestTask = await TestTask.find_one_by(job_id=task_id)
    if not test_task:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "测试任务不存在"})
    await test_task.start(scheduler=scheduler)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "测试任务开始"}) 


@router.post("/call", summary="启动一个一次性打卡任务")
async def call_task(call_task_info: CallPunchTaskIn, user: "User" = Depends(get_current_active_user)):
    punch_task: PunchTask = PunchTask(**{
        "session_id": user.session_id,
        "user_account": user.user_account,
        "login_token": user.login_token,
        **call_task_info.dict(exclude_unset=True),
        "user_id": user.id
    })
    await punch_task.run_once()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "打卡任务执行成功"})


@router.post("/trigger/{task_id}", summary="通过id马上触发任务")
async def trigger_task_by_id(task_id: int, user: "User" = Depends(get_current_active_user)):
    """
    未完善的方法，这里只是简单的触发任务，没有考虑任务的类型
    """
    task: PunchTask = await PunchTask.find_by_id(task_id)
    if not task:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "任务不存在"})
    if task.user_id != user.id and not user.is_admin:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "无权触发该任务"})
    await task.run(call_immediately=True)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "触发成功"})


@router.delete("/{task_type}/{task_id}", response_description="删除一个打卡任务", summary="通过id删除一个打卡任务")
async def delete_task(task_type: "TaskType", task_id: int, user: "User" = Depends(get_current_active_user)):
    cls: TaskBase = task_type.get_task_class()
    task: TaskBase = await cls.find_by_id(task_id)
    if not task:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "该打卡任务不存在"})
    if task.user_id != user.id and not user.is_admin:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": "无权删除该任务"})
    if job := scheduler.get_job(task.job_id):
        scheduler.remove_job(cast("Job", job).id)
    await task.delete()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "删除成功"})


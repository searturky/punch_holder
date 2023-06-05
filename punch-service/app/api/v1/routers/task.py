from collections import defaultdict
from app.crud.user import get_user, get_current_active_user
from fastapi import APIRouter, Body, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from app.models.api.register import RegisterPunchTaskIn, RegisterTestTaskIn
from app.schemas.api.task import TestTask, PunchTask
from app.schemas.api.user import User
from app.scheduler import scheduler


router = APIRouter()


@router.post("/punch", response_description="注册一个新打卡任务")
async def register_punch_task(punch_task_info: RegisterPunchTaskIn = Body(...), user: User = Depends(get_current_active_user)):
    punch_task: PunchTask = PunchTask(**{
        "session_id": user.session_id,
        "user_account": user.user_account,
        "login_token": user.login_token,
        **punch_task_info.dict(),
        "user_id": user.id
    })
    await punch_task.save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "打卡任务注册成功"})


@router.post("/test", response_description="注册一个新测试任务")
async def register_test_task(test_task_info: RegisterTestTaskIn = Body(...), user: User = Depends(get_current_active_user)):
    test_task = TestTask(**test_task_info.dict(), user_id=user.id)
    await test_task.save()
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "测试任务注册成功"})


@router.get("/test/start/{task_id}", response_description="通过id开始一个测试任务")
async def start_test_task_by_id(task_id: str, user: User = Depends(get_current_active_user)):
    test_task: TestTask = await TestTask.find_one_by(job_id=task_id)
    if not test_task:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "测试任务不存在"})
    await test_task.start(scheduler=scheduler)
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "测试任务开始"})


# @router.delete("/register/{register_id}", response_description="删除一个打卡任务")
# async def delete_register(register_id: str):
#     return JSONResponse(status_code=status.HTTP_200_OK)

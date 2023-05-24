from collections import defaultdict
from app.crud.register import is_register
from app.crud.user import get_user
from app.database import db
from fastapi import APIRouter, Body, Depends, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from app.models.api.register import RegisterIn, Register
from app.models.api.user import User
from pymongo import ReturnDocument


router = APIRouter()


@router.post("", response_description="注册一个新打卡任务")
async def register(register_info: RegisterIn = Body(...)):
    user: User = await get_user(db, register_info.token)
    if not user:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "token未注册"})
    if is_register(db, user.token, ):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "任务已经注册过了"})
    register = Register(**register_info.dict())
    await db["register"].insert_one(jsonable_encoder(register))
    return JSONResponse(status_code=status.HTTP_201_CREATED)


@router.get("/register/all", response_description="获取所有打卡任务")
async def get_all_register(request: Request):
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.delete("/register/{register_id}", response_description="删除一个打卡任务")
async def delete_register(register_id: str):
    return JSONResponse(status_code=status.HTTP_200_OK)

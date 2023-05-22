from collections import defaultdict

from app.database import db
from fastapi import APIRouter, Body, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from app.models.api.register import RegisterIn
from pymongo import ReturnDocument

router = APIRouter()

@router.post("/register", response_description="注册一个新打卡任务")
async def register(register_info: RegisterIn = Body(...), response_model=RegisterIn):

    return JSONResponse(status_code=status.HTTP_201_CREATED)


@router.get("/register/all", response_description="获取所有打卡任务")
async def get_all_register():
    return JSONResponse(status_code=status.HTTP_200_OK)


@router.delete("/register/{register_id}", response_description="删除一个打卡任务")
async def delete_register(register_id: str):
    return JSONResponse(status_code=status.HTTP_200_OK)

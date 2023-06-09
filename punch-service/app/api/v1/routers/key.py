from typing import List
from app.crud.user import get_current_active_super_user, get_current_active_admin_user
from app.crud.key import get_key, create_new_key_by_type
from fastapi import APIRouter, Body, Request, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from app.models.api.key import KeyIn
from app.schemas.api.user import User
from app.schemas.api.key import Key

router = APIRouter()


@router.post("", description="生成新key", summary="生成新key")
async def create_new_key(create_key_info: KeyIn = Body(...), user: User = Depends(get_current_active_super_user)):
    if await create_new_key_by_type(create_key_info.type):
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "key生成成功"})
    return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "key生成失败，请稍后重试"})


@router.get("/all", description="获取所有key信息", summary="获取所有key信息")
async def get_all_key(user: User = Depends(get_current_active_admin_user)):
    keys: List["Key"] = await Key.find_all()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"keys": [key.to_dict(exclude={"create_at", "update_at"}) for key in keys]})


@router.get("/{key_code}", description="查询key是否已经注册", summary="查询key是否已经注册")
async def get_key_info(key_code: str):
    key = await get_key(key_code)
    if not key:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "未查询到该key"})
    if key.bound:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "该key已经被使用"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "该key可以使用"})
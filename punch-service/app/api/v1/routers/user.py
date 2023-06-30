from typing import List
from app.crud.user import (
    get_current_active_user, 
    get_user, create_user, 
    get_current_active_admin_user,
    create_user,
)
from fastapi import APIRouter, Body, Request, status, Depends
from fastapi.responses import JSONResponse, Response
from app.models.api.user import CreateUserIn, UpdateUserIn
from app.schemas.api.user import User
from app.utils.common import get_password_hash
from app.crud.key import get_key

router = APIRouter()
router.tags = ["用户"]

@router.post("", description="新用户注册", summary="新用户注册")
async def create_new_user(create_user_info: CreateUserIn = Body(...)):
    key = await get_key(create_user_info.key_code)
    if not key or key.bound:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "key未注册或已经被使用"})
    if await get_user(create_user_info.username):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "用户已经注册过了"})
    
    hashed_password = get_password_hash(create_user_info.password)
    user = User(**{
        "username": create_user_info.username,
        "password": hashed_password,
        "key_id": key.id,
    })
    user = await create_user(user, key)
    if not user:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "用户注册失败，请稍后重试"})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"detail": "用户注册成功"})


@router.put("", description="修改用户信息", summary="修改用户信息")
async def update_user(update_info: UpdateUserIn = Body(...), user: User = Depends(get_current_active_user)):
    update_info: dict = update_info.dict(exclude_unset=True)
    if password := update_info.get("password"):
        update_info["password"] = get_password_hash(password)
    user.update(update_info)
    await user.save()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "用户信息修改成功"})


@router.get("", description="获取当前用户信息", summary="获取当前用户信息")
async def get_user_info(user: User = Depends(get_current_active_user)):
    res_user = user.to_dict(exclude={"password", "key_id", "create_at", "update_at"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"user": res_user})


@router.get("/all", description="获取所有用户信息", summary="获取所有用户信息")
async def get_all_user(user: User = Depends(get_current_active_admin_user)):
    users: List["User"] = await User.find_all()
    res_users = [user.to_dict(exclude={"password", "key_id", "create_at", "update_at"}) for user in users]
    return JSONResponse(status_code=status.HTTP_200_OK, content={"users": res_users})


@router.delete("/{user_id}", description="通过id删除用户", summary="通过id删除用户")
async def delete_user_by_id(user_id: int, user: User = Depends(get_current_active_admin_user)):
    delete_user = await User.find_by_id(user_id)
    if not delete_user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "用户不存在"})
    await delete_user.delete()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "用户删除成功"})


@router.get("/{user_id}", description="通过id获取用户信息", summary="通过id获取用户信息")
async def get_user_info_by_id(user_id: int, user: User = Depends(get_current_active_admin_user)):
    res_user = await User.find_by_id(user_id)
    if not res_user:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "用户不存在"})
    res_user = res_user.to_dict(exclude={"password", "key_id", "create_at", "update_at"})
    return JSONResponse(status_code=status.HTTP_200_OK, content={"user": res_user})
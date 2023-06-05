from app.crud.user import get_current_active_user, get_user, create_user
from fastapi import APIRouter, Body, Request, status, Depends
from fastapi.responses import JSONResponse, Response
from app.models.api.user import CreateUserIn, UpdateUserIn
from app.schemas.api.user import User
from app.utils.common import get_password_hash
from app.crud.user import create_user
from app.crud.key import get_key

router = APIRouter()


@router.post("", response_description="新用户注册")
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


@router.put("", response_description="修改用户信息")
async def update_user(update_info: UpdateUserIn = Body(...), user: User = Depends(get_current_active_user)):
    update_info: dict = update_info.dict(exclude_unset=True)
    if update_info.get("password"):
        update_info["password"] = get_password_hash(update_info["password"])
    user.update(update_info)
    await user.save()
    return JSONResponse(status_code=status.HTTP_200_OK, content={"detail": "用户信息修改成功"})


# @router.get("/all/{super_token}", response_description="获取所有用户信息")
# async def all_user(request: Request, super_token: str):
#     user = request.user
#     if not user.is_authenticated or not user.is_admin:
#         return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "token校验失败"})
#     users = await get_all_user(db)
#     return JSONResponse(status_code=status.HTTP_200_OK, content={"users": users})
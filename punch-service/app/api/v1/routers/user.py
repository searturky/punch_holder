from collections import defaultdict
from app.crud.user import get_user, get_all_user, create_user
from app.crud.key import get_key, bound_key
from fastapi import APIRouter, Body, Request, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from app.models.api.user import UserInDB, CreateUserIn
from app.utils.common import get_password_hash

router = APIRouter()


@router.post("", response_description="新用户注册")
async def create_user(create_user_info: CreateUserIn = Body(...)):
    key = await get_key(create_user_info.key_code)
    if not key or key.bound:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "key未注册或已经被使用"})
    if await get_user(db, create_user_info.username):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "用户已经注册过了"})
    
    hashed_password = get_password_hash(create_user_info.password)
    user = UserInDB(**create_user_info.dict(), key=key, hashed_password=hashed_password)
    
    await create_user(db, user)
    await bound_key(db, key.key)
    return JSONResponse(status_code=status.HTTP_201_CREATED)


# @router.put("", response_description="修改用户信息")
# async def update_user(update_info: UserIn = Body(...)):
#     user: User = await get_user(db, update_info.token)
#     if not user:
#         return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "token未注册"})
#     if is_register(db, user.token, ):
#         return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "任务已经注册过了"})
#     register = Register(**register_info.dict())
#     await db["register"].insert_one(jsonable_encoder(register))
#     return JSONResponse(status_code=status.HTTP_201_CREATED)


# @router.get("/all/{super_token}", response_description="获取所有用户信息")
# async def all_user(request: Request, super_token: str):
#     user = request.user
#     if not user.is_authenticated or not user.is_admin:
#         return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "token校验失败"})
#     users = await get_all_user(db)
#     return JSONResponse(status_code=status.HTTP_200_OK, content={"users": users})
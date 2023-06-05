from collections import defaultdict
from app.crud.user import get_user, get_all_user, create_user
from app.crud.key import get_key
from fastapi import APIRouter, Body, Request, status, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from app.models.api.key import KeyIn
from app.utils.common import get_password_hash

router = APIRouter()


@router.get("", response_description="查询key是否已经注册")
async def get_key_info(key_info: KeyIn = Body(...)):
    key = await get_key(create_user_info.key)
    if not key or key.bound:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "key未注册或已经被使用"})
    if await get_user(db, create_user_info.username):
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": "用户已经注册过了"})
    
    hashed_password = get_password_hash(create_user_info.password)
    user = UserInDB(**create_user_info.dict(), key=key, hashed_password=hashed_password)
    
    await create_user(db, user)
    await bound_key(db, key.key)
    return JSONResponse(status_code=status.HTTP_201_CREATED)


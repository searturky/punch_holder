from inspect import signature
from functools import wraps
from fastapi.responses import JSONResponse
from fastapi import Request, status
from app.crud.user import get_user
from app.models.api.user import User


def token_check(api_func=None):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            request: Request = args[0]
            token = request.headers.get("token")
            user: User = await get_user(token)
            if not user:
                return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "token未注册"})
            return await func(*args, **kwargs)
        return wrapper
    return decorator
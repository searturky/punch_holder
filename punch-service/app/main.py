import asyncio
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from app.api.router import router
from app.core.config import settings
from app.scheduler import scheduler
from app.crud.common import init_db


def get_application():
    _app = FastAPI(title=settings.PROJECT_NAME)

    @_app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            dict(detail=exc.errors()),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    _app.include_router(router, prefix="/api")
    init_db(settings.SUPERUSER_KEY)
    scheduler.start()

    return _app

app = get_application()


# 登录 POST https://goalgo-gateway.holderzone.com/login

# 登出 POST https://goalgo-gateway.holderzone.com/login

# s_id_1 = '075c8ad40f71fd50d7f1bc7c7fa43c80dba21ffa'

# async def main():
#     cookies = {"session_id": s_id_1}
#     login_token = "a1701b16-7774-4a64-8d7f-7df442372500"
#     user_account = "18602876620"
#     punch_info: TodayPunchInfo = await TodayStaticId.request(
#         login_token=login_token,
#         user_account=user_account,
#         cookies=cookies
#     )
#     static_id = punch_info.static_id
#     today_morning_info: MorningInfo = punch_info.morning_info
#     today_afternoon_info: AfternoonInfo = punch_info.afternoon_info
#     print('static_id', static_id)
#     res = await PunchIn.request(
#         login_token=login_token,
#         user_account=user_account,
#         punch_type=PunchInType.AFTERNOON,
#         static_id=static_id,
#         cookies=cookies
#     )
#     ...


# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(main())


import datetime
# from fastapi import FastAPI, Request, status
# from fastapi.responses import JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import ValidationError
# from app.api.router import router
# from app.core.config import settings
from httpx import AsyncClient

# def get_application():
#     _app = FastAPI(title=settings.PROJECT_NAME)

#     @_app.exception_handler(ValidationError)
#     async def validation_error_handler(request: Request, exc: ValidationError):
#         return JSONResponse(
#             dict(detail=exc.errors()),
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         )

#     _app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

#     _app.include_router(router, prefix="/api")

#     return _app

# app = get_application()

# 打卡信息查询 GET
f"https://zkz.holderzone.com/card/come_in?target_date=2023-05-15&user_account=17602891419"

# 登录 POST https://goalgo-gateway.holderzone.com/login

# 登出 POST https://goalgo-gateway.holderzone.com/login

# 上班卡seesion_id  POST
url = f"https://zkz.holderzone.com/card/punch_in"
s_id_1 = "1189f9a735e1c25a15da6c10c4dc29cd47a21099"
header_1 = {
    "Host": "zkz.holderzone.com",
    "languages": "zh_CN",
    "system": "oa",
    "version": 169,
    "Accept": "*/*",
    "Accept-Language": "zh-Hans-CN;q=1.0, en-CN;q=0.9",
    "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
    "Content-Type": "application/json",
    "loginToken": "86bbe5ad-e5de-4605-b20a-517b27e6e10f",
    "User-Agent": "GoalgoMaster/1.6.9 (com.holder.app.goalgo.Goalgo; build:1; iOS 16.3.1) Alamofire/5.5.0",
    "Connection": "keep-alive",
    "hardware": "ios",
    "companyId": 244
}
cookie_1 = {
    "session_id": "1189f9a735e1c25a15da6c10c4dc29cd47a21099"
}
body_1 = {
  "card_choice" : 1,
  "work_order_chooce_id" : "",
  "card_equipment" : "",
  "httpWithoutRpc" : 1,
  "card_wifi" : "10",
  "statistic_id" : 160211,
  "card_point" : "09:00:00",
  "point_morrow" : False,
  "card_remark" : "",
  "card_image" : "",
  "target_date" : "2023-05-15",
  "card_type" : "morning",
  "belong_day" : "2023-05-15",
  "user_account" : "18602876620",
  "outside_office" : False,
  "card_address" : ""
}

# 下班卡seesion_id
s_id_2 = "1189f9a735e1c25a15da6c10c4dc29cd47a21099"
header_2 = {
    "Host": "zkz.holderzone.com",
    "languages": "zh_CN",
    "system": "oa",
    "version": 169,
    "Accept": "*/*",
    "Accept-Language": "zh-Hans-CN;q=1.0, en-CN;q=0.9",
    "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
    "Content-Type": "application/json",
    "loginToken": "86bbe5ad-e5de-4605-b20a-517b27e6e10f",
    "User-Agent": "GoalgoMaster/1.6.9 (com.holder.app.goalgo.Goalgo; build:1; iOS 16.3.1) Alamofire/5.5.0",
    "Connection": "keep-alive",
    "hardware": "ios",
    "companyId": 244,
}
cookie_2 = {
    "session_id": "1189f9a735e1c25a15da6c10c4dc29cd47a21099"
}
body_2 = {
  "card_choice" : 2,
  "card_equipment" : "",
  "httpWithoutRpc" : 1,
  "work_order_chooce_id" : "",
  "card_wifi" : "",
  "statistic_id" : 160211,
  "belong_day" : "2023-05-15",
  "card_remark" : "",
  "point_morrow" : False,
  "card_image" : "",
  "target_date" : "2023-05-15",
  "card_type" : "afternoon",
  "card_point" : "18:30:00",
  "user_account" : "18602876620",
  "outside_office" : False,
  "card_address" : "成都市武侯区凯乐国际-2幢&成都市武侯区凯乐国际-2幢"
}

async def logout(http_client: AsyncClient):
    ...

async def main():
    from http_client import get_http_client
    today = str(datetime.date.today())
    body_1['target_date'] = today
    body_1['belong_day'] = today
    header_1['loginToken'] = "a1701b16-7774-4a64-8d7f-7df442372500"
    async with get_http_client() as http_client:
        http_client: AsyncClient
        response = await http_client.post(
            url=url,
            cookies={"session_id": s_id_1},
            headers=header_1,
            json=body_1,
        )

        print(response.json)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
    # async with get_http_client() as http_client:


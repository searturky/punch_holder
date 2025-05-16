import re
import random
import logging
from datetime import datetime
from enum import Enum
from typing import Tuple
from app.http_client import get_http_client
from app.utils.time_util import get_local_today_date_str, local_now
from httpx import AsyncClient, Response


logger = logging.getLogger("uvicorn")


class PunchInType(str, Enum):
    AFTERNOON = "afternoon"
    MORNING = "morning"

    @classmethod
    def get_card_choice(cls, punch_type: "PunchInType"):
        return "1" if punch_type == cls.MORNING else "2"
    
    @classmethod
    def get_card_point(cls, punch_type: "PunchInType"):
        return "09:00:00" if punch_type == cls.MORNING else "18:30:00"


class ApiURLs(str, Enum):

    TodayStaticId = "https://zkzoa.holderzone.com/card/come_in"
    PunchIn = "https://zkzoa.holderzone.com/card/punch_in"
    PunchDCIn = "https://kq.daochen.com/api/AttendanceManagement/clock-in/create"
    DCJWT = "https://notify.cddc56.com/WeixinUser/DecodeInfo"


class PunchDCJWT():
    _url = ApiURLs.DCJWT
    _headers = {
        "Host": "notify.cddc56.com", 
        "Content-type": "application/json",
        "Accept-Encoding": "gzip, deflate, br",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.57(0x1800392b) NetType/WIFI Language/zh_CN",
        "Referer": "https://servicewechat.com/wxa71ddd1b81c2fab7/78/page-frame.html"
    }
    _body = {
        "weappid": "wxa71ddd1b81c2fab7",
        "vi": "n6zdY33axvgpT6yocJBsig==",
        "isjwt": True,
        "unionid": "onrOR53KJGoEN6QK93tAq_4cjSiE",
        "encryptedData": "L1EuZl7piFPKb5tFr3PD7wpL59X1Cv91BuKfKf6Eec875nkcHJTPH0+MDW9p+WQIPFAk/IlLGoPtHPMnB+FK32F/+3kDUdzPZmhuF/7gKB8lLGRcFiv4vnIVYjzpuDgNBE9Y94U8b/ltNo0jQD69UWkQvbUM8k/4Wb/WHUiPsaXIzO/PRZPW4h6XjKkV32wIiPbIgJmkyFrdAE3LwiPS7Do1rP96ZU2ebIRg3mIrx9SyTs042BFwBG0d/aRq7qvvRRUgActMr6cCzHbreYIp72KzF2nK8vx/BImSQXHjfrBEmDdTjIoaW7/M55KbFoTSjtfPcY99rMFPD1242Kmt6IUQhv8D0hO4lrl6y/R+czWR7Qgd0PFGbusV5Xmm4nHUXgaVxNJSxjmB6Th5HPORczABc8741TNQSi9YGzV6BikK53YOanTerMRCk5pNeZAxOB9Fj87EqRODhuESodOaSOi/h4naeJ0a9lg+dR9j5qFHeBSUrNh+3M8JZmUpLbnWZXlZMF+JKZZbo3OVahM2Aw=="
    }

    def prepare_base64(base64_str):
        # 清理非法字符并修复填充
        cleaned = re.sub(r'[^A-Za-z0-9+/=]', '', base64_str.replace('\\', ''))
        padding = len(cleaned) % 4
        if padding:
            cleaned += '=' * (4 - padding)
        return cleaned

    @classmethod
    async def request(cls) -> Response:
        prepare_base64 = cls.prepare_base64(cls._body["encryptedData"])
        cls._body["encryptedData"] = prepare_base64
        async with get_http_client() as http_client:
            http_client: AsyncClient
            res = await http_client.post(
                url=cls._url,
                headers=cls._headers,
                json=cls._body,
            )
            assert res.status_code == 200, 'Request failed'
            return res

class PunchDCIn():
    _url = ApiURLs.PunchDCIn
    _headers = {
        "Host": "kq.daochen.com",
        "Accept": "application/json",
        "Authorization": None,
        "Sec-Fetch-Site": "same-site",
        "Accept-Language": "zh-Hans",
        "Accept-Encoding": "gzip, deflate, br",
        "Sec-Fetch-Mode": "cors",
        "Content-Type": "application/json; charset=utf-8",
        "Origin": "https://m.daochen.com",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_3_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.57(0x1800392b) NetType/4G Language/zh_CN miniProgram/wxa71ddd1b81c2fab7",
        "Referer": "https://m.daochen.com/",
        "Sec-Fetch-Dest": "empty",
    }
    _body = {
        "lng" : 104.07648268670816,
        "lat" : 30.686807826963463,
        "clockInType" : 0,
        "clockInDate" : "2025-04-02T08:54:15.387",
        "address" : "四川省成都市金牛区新村河边街15-1号"
    }
    ING = 104.07648268670816
    LAT = 30.686807826963463

    @classmethod
    async def request(cls, clockin_type: int, authorization: str) -> Response:
        clock_n_date = local_now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        headers = {
            **cls._headers,
            "Authorization": authorization
        }
        random_ing = cls.ING + random.uniform(-0.0000000000001, 0.0000000000001)
        random_lat = cls.LAT + random.uniform(-0.0000000000001, 0.0000000000001)
        body = {
            **cls._body,
            "lng": random_ing,
            "lat": random_lat,
            "clockInType": int(clockin_type),
            "clockInDate": clock_n_date
        }
        async with get_http_client() as http_client:
            http_client: AsyncClient
            res = await http_client.post(
                url=cls._url,
                headers=headers,
                json=body,
            )
            assert res.status_code == 200, 'Request failed'
            return res


class PunchIn():

    _url = ApiURLs.PunchIn
    _headers = {
        "Host": "zkzoa.holderzone.com",
        "languages": "zh_CN",
        "system": "oa",
        "version": "169",
        "Accept": "*/*",
        "Accept-Language": "zh-Hans-CN;q=1.0, en-CN;q=0.9",
        "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        "Content-Type": "application/json",
        "User-Agent": "GoalgoMaster/1.6.9 (com.holder.app.goalgo.Goalgo; build:1; iOS 16.3.1) Alamofire/5.5.0",
        "Connection": "keep-alive",
        "hardware": "ios",
        "companyId": "244"
    }
    _body = {
        "work_order_chooce_id" : "",
        "card_equipment" : "",
        "httpWithoutRpc" : "1",
        "card_wifi" : "10",
        "point_morrow" : False,
        "card_remark" : "",
        "card_image" : "",
        "outside_office" : False,
        "card_address" : ""
    }

    @classmethod
    async def request(cls, user_account:str, punch_type: PunchInType, static_id: int, login_token:str, session_id:str, card_point:str=None, cookies: dict=None, headers: dict=None, body: dict=None) -> Response:
        today_str = get_local_today_date_str()
        async with get_http_client() as http_client:
            http_client: AsyncClient
            res = await http_client.post(
                url=cls._url,
                cookies=cookies or {"session_id": session_id},
                headers=headers or {**cls._headers, "loginToken": login_token},
                json=body or {
                    **cls._body, 
                    'statistic_id': str(static_id),
                    'card_choice' : PunchInType.get_card_choice(punch_type),
                    'card_point': card_point or PunchInType.get_card_point(punch_type),
                    'target_date': today_str,
                    'belong_day': today_str,
                    'user_account': user_account,
                    'card_type': punch_type.value,
                },
            )
            assert res.status_code == 200, 'Request failed'
            return res

    @classmethod
    def should_punch_in(cls, today_punch_info: "TodayPunchInfo") -> Tuple[bool, PunchInType, str]:
        if today_punch_info.is_rest:
            return False, None, None
        today_morning_info: MorningInfo = today_punch_info.morning_info
        today_afternoon_info: AfternoonInfo = today_punch_info.afternoon_info
        local_now_time = local_now()
        local_now_time_str = local_now_time.strftime("%H:%M:%S")
        logging.info(f"===============local_now_time_str:=================== {local_now_time_str}")
        logging.info(f"===============today_morning_info.point=================== {today_morning_info.point}")
        logging.info(f"===============today_afternoon_info.point=================== {today_afternoon_info.point}")
        if local_now_time_str < today_morning_info.point and not today_morning_info.is_punch_in:
            logging.info("===============Should Punch Morning===================")
            return True, PunchInType.MORNING, today_morning_info.point
        if local_now_time_str > today_afternoon_info.point and not today_afternoon_info.is_punch_in:
            logging.info("===============Should Punch Afternoon===================")
            return True, PunchInType.AFTERNOON, today_afternoon_info.point
        return False, None, None


class MorningInfo():

    def __init__(self, info: dict):
        self._info = info
        self.info_type = PunchInType.MORNING
        self.point = info.get("point") or "09:00:00"
        self.card_address = info.get("card_address") or ""

    @property
    def punch_in_time(self) -> str:
        return self._info.get("time")

    @property
    def punch_in_is_active(self) -> bool:
        return self._info.get("active", False)

    @property
    def is_punch_in(self) -> bool:
        return self.punch_in_time != False or self._info.get("state") == "done"
    

class AfternoonInfo():
    
    def __init__(self, info: dict):
        self._info = info
        self.info_type = PunchInType.AFTERNOON
        self.point = info.get("point") or "18:30:00"
        self.card_address = info.get("card_address") or ""

    @property
    def punch_in_time(self) -> str:
        return self._info.get("time")

    @property
    def punch_in_is_active(self) -> bool:
        return self._info.get("active", False)

    @property
    def is_punch_in(self) -> bool:
        return self.punch_in_time != False or self._info.get("state") == "done"


class TodayPunchInfo():

    def __init__(self, res: "Response"):
        self.res_json: dict = res.json()
        morning_info: list = self.res_json.get("data", {}).get("card_history", {}).get("morning", [])
        afternoon_info: list = self.res_json.get("data", {}).get("card_history", {}).get("afternoon", [])
        self.session_id: str = res.cookies.get("session_id")
        self.is_rest: bool = True if self.res_json.get("data", {}).get("card_state") == 'rest' else False
        self.static_id: int = self.res_json.get("data", {}).get("id")
        self.morning_info = MorningInfo(morning_info[0]) if len(morning_info) > 0 else None
        self.afternoon_info = AfternoonInfo(afternoon_info[0]) if len(afternoon_info) > 0 else None


class TodayStaticId():

    _url = ApiURLs.TodayStaticId
    _headers = {
        "Host": "zkzoa.holderzone.com",
        "languages": "zh_CN",
        "system": "oa",
        "version": "169",
        "Accept": "*/*",
        "Accept-Language": "zh-Hans-CN;q=1.0, en-CN;q=0.9",
        "Accept-Encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8",
        "User-Agent": "GoalgoMaster/1.6.9 (com.holder.app.goalgo.Goalgo; build:1; iOS 16.3.1) Alamofire/5.5.0",
        "Connection": "keep-alive",
        "hardware": "ios",
        "companyId": "244"
    }

    @classmethod
    async def request(cls, login_token:str, user_account:str, session_id:str, cookies: dict=None, headers: dict=None) -> Tuple["TodayPunchInfo", "Response"]:
        async with get_http_client() as http_client:
            http_client: AsyncClient
            res = await http_client.get(
                url=cls._url,
                cookies=cookies or {"session_id": session_id},
                headers=headers or {**cls._headers, "loginToken": login_token},
                params={
                    "target_date": get_local_today_date_str(),
                    "user_account": user_account
                }
            )
            assert res.status_code == 200, 'Request failed'
            return TodayPunchInfo(res), res
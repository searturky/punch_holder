from enum import Enum
from http_client import get_http_client
from utils.holder_api_args import get_today_date_str
from httpx import AsyncClient


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

    TodayStaticId = "https://zkz.holderzone.com/card/come_in"
    PunchIn = "https://zkz.holderzone.com/card/punch_in"


class PunchIn():

    _url = ApiURLs.PunchIn
    _headers = {
        "Host": "zkz.holderzone.com",
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
    async def request(cls, user_account:str, punch_type: PunchInType, static_id: int, login_token:str, cookies: dict=None, headers: dict=None, body: dict=None):
        today_str = get_today_date_str()
        async with get_http_client() as http_client:
            http_client: AsyncClient
            res = await http_client.post(
                url=cls._url,
                cookies=cookies,
                headers=headers or {**cls._headers, "loginToken": login_token},
                json=body or {
                    **cls._body, 
                    'statistic_id': str(static_id),
                    'card_choice' : PunchInType.get_card_choice(punch_type),
                    'card_point': PunchInType.get_card_point(punch_type),
                    'target_date': today_str,
                    'belong_day': today_str,
                    'user_account': user_account,
                    'card_type': punch_type.value,
                },
            )
            assert res.status_code == 200, 'Request failed'
            return res.json()


class MorningInfo():

    def __init__(self, info: dict):
        self._info = info
        self.info_type = PunchInType.MORNING

    @property
    def punch_in_time(self) -> str | bool:
        return self._info.get("time")

    @property
    def punch_in_is_active(self) -> str:
        return self._info.get("active")

    @property
    def is_punch_in(self) -> bool:
        return self.punch_in_time != False or self._info.get("state") == "done"
    

class AfternoonInfo():
    
        def __init__(self, info: dict):
            self._info = info
            self.info_type = PunchInType.AFTERNOON
    
        @property
        def punch_in_time(self) -> str | bool:
            return self._info.get("time")
    
        @property
        def punch_in_is_active(self) -> str:
            return self._info.get("active")
    
        @property
        def is_punch_in(self) -> bool:
            return self.punch_in_time != False or self._info.get("state") == "done"


class TodayStaticId():

    _url = ApiURLs.TodayStaticId
    _headers = {
        "Host": "zkz.holderzone.com",
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
    async def request(cls, login_token:str, user_account:str, cookies: dict=None, headers: dict=None):
        async with get_http_client() as http_client:
            http_client: AsyncClient
            res = await http_client.get(
                url=cls._url,
                cookies=cookies,
                headers=headers or {**cls._headers, "loginToken": login_token},
                params={
                    "target_date": get_today_date_str(),
                    "user_account": user_account
                }
            )
            assert res.status_code == 200, 'Request failed'
            today_morning_info = MorningInfo(res.json().get("data").get("card_history").get("morning")[0])
            today_afternoon_info = AfternoonInfo(res.json().get("data").get("card_history").get("afternoon")[0])
            return {
                'today_static_id': res.json().get("data").get("id"),
                'today_morning_info': today_morning_info,
                'today_afternoon_info': today_afternoon_info
            }
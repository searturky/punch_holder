import pytz
import datetime
from app.core.config import settings


tzinfo = pytz.timezone(settings.TIMEZONE)


def get_local_today_date_str() -> str:
    return datetime.datetime.now(tzinfo).strftime("%Y-%m-%d")


def local_now() -> datetime.datetime:
    return datetime.datetime.now(tzinfo)
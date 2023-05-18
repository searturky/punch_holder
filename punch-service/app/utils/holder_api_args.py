from datetime import datetime
from random import randint


def get_today_date_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def generate_punch_in_morning_time() -> datetime:
    datee = datetime.fromisoformat(f"{get_today_date_str()} 08:{randint(30, 59)}:00")
    return datee

def generate_punch_in_afternoon_time() -> datetime:
    datee = datetime.fromisoformat(f"{get_today_date_str()} 18:{randint(40, 59)}:00")
    return datee

if __name__ == '__main__':
    print(generate_punch_in_afternoon_time())
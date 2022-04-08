import pytz
from datetime import datetime


kiev_tz = pytz.timezone('Europe/Kiev')


def now():
    return datetime.now(tz=kiev_tz)


def now_day():
    return now().date()

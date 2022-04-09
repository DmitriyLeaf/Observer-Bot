import pytz
from datetime import datetime


class DateTime:
    kiev_tz = pytz.timezone('Europe/Kiev')

    @staticmethod
    def now():
        return datetime.now(tz=DateTime.kiev_tz)

    @staticmethod
    def now_day():
        return DateTime.now().date()

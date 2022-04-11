from enum import Enum

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


class EnumTool(Enum):
    @staticmethod
    def cases(cls):
        return list(map(lambda c: c, cls))

    @staticmethod
    def values(cls) -> [str]:
        return list(map(lambda c: c.value, cls))

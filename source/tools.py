from enum import Enum

import pytz
from datetime import datetime


class DateTime:
    kiev_tz = pytz.timezone('Europe/Kiev')

    @classmethod
    def now(cls):
        return datetime.now(tz=cls.kiev_tz)

    @classmethod
    def now_day(cls):
        return cls.now().date()


class EnumTool(Enum):
    @classmethod
    def cases(cls):
        return list(map(lambda c: c, cls))

    @classmethod
    def values(cls) -> [str]:
        return list(map(lambda c: c.value, cls))

    @classmethod
    def last(cls):
        return cls.cases()[-1]

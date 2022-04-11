import json
from enum import Enum
from typing import Optional
from datetime import datetime
from constants import Delay, Stage

from telegram import User


class BaseModel:
    def to_json(self) -> str:
        return json.dumps(self, indent=4, default=lambda o: o.__dict__)

    def to_dict(self) -> dict:
        return json.loads(self.to_json())

    def to_list(self) -> list:
        return list(self.to_dict().values())

    @staticmethod
    def decode_json(cls, string: str):
        data = json.loads(string)
        return cls(**data)

    @staticmethod
    def decode_dict(cls, d: dict):
        jsn = json.dumps(d)
        return cls.decode_json(cls, jsn)


class Admin(BaseModel):
    class KeysId(int, Enum):
        aid = 0
        username = 1
        token = 2
        observing = 3
        delay = 4
        critical_only = 5
        stage = 6
        sub_stage = 7

    def __init__(
            self,
            aid: int = -1,
            username: str = "",
            token: str = "",
            observing: bool = False,
            delay: Delay = Delay.one,
            critical_only: bool = False,
            stage: Stage = Stage.HELLO,
            sub_stage: Stage = Stage.HELLO
    ):
        self.aid: int = int(aid)
        self.username: str = username
        self.token: str = token
        self.observing: bool = observing
        self.delay: Delay = delay
        self.critical_only: bool = critical_only
        self.stage: Stage = stage
        self.sub_stage: Stage = sub_stage


class Service(BaseModel):
    def __init__(self):
        self.id: int = -1
        self.name: str = ""
        self.link: str = ""
        self.is_additional: bool = False


class Report:
    def __init__(self):
        self.id: int = -1
        self.service_id: int = -1
        self.status: int = -1
        self.duration: int = -1
        self.additional: str = ""
        self.datetime: Optional[datetime] = None

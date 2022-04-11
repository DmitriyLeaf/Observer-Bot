import json
from enum import Enum
from typing import Optional
from datetime import datetime
from constants import Delay, Stage

from telegram import User


class BaseModel:
    def to_json(self):
        return json.dumps(self, indent=4, default=lambda o: o.__dict__)

    def to_dict(self):
        return json.loads(self.to_json())

    @staticmethod
    def decode(cls, string: str):
        data = json.loads(string)
        return cls(**data)


class Admin(BaseModel):
    def __init__(
            self,
            aid: int = -1,
            tg_user: Optional[User] = None,
            token: str = "",
            observing: bool = False,
            delay: Delay = Delay.one,
            critical_only: bool = False,
            stage: Stage = Stage.HELLO,
            sub_stage: Stage = Stage.HELLO
    ):
        self.aid: int = aid
        self.tg_user: Optional[User] = tg_user
        self.token: str = token
        self.observing: bool = observing
        self.delay: Delay = delay
        self.critical_only: bool = critical_only
        self.stage: Stage = stage
        self.sub_stage: Stage = sub_stage

        if aid < 0 and tg_user is not None:
            self.aid = tg_user.id


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

import json
from enum import Enum
from tools import EnumTool
from typing import Optional
from datetime import datetime
from constants import Delay, Stage, MessageKeys

from telegram import User


class BaseModel:
    class KeysId(int, EnumTool):
        kid = 0

    def to_json(self) -> str:
        return json.dumps(self, indent=4, default=lambda o: o.__dict__)

    def to_dict(self) -> dict:
        return json.loads(self.to_json())

    def to_list(self) -> list:
        return list(self.to_dict().values())

    @classmethod
    def decode_json(cls, string: str):
        data = json.loads(string)
        # return super(BaseModel, cls).__new__(cls, **data)
        return cls(**data)

    @classmethod
    def decode_dict(cls, d: dict):
        jsn = json.dumps(d)
        return cls.decode_json(jsn)

    @classmethod
    def decode_list(cls, lst: list):
        keys = cls().__dict__.keys()
        dct = dict(zip(keys, lst))
        return cls.decode_dict(dct)

    def get_id(self) -> int:
        s_type = type(self)
        if s_type == Admin:
            return self.aid
        elif s_type == Service:
            return self.sid
        elif s_type == Report:
            return self.rid

    def get_key_id(self) -> KeysId:
        s_type = type(self)
        if s_type == Admin:
            return self.KeysId.aid
        elif s_type == Service:
            return self.KeysId.sid
        elif s_type == Report:
            return self.KeysId.rid


class Admin(BaseModel):
    class KeysId(int, EnumTool):
        aid = 0
        username = 1
        token = 2
        observing = 3
        delay = 4
        critical_only = 5
        stage = 6
        sub_stage = 7

        def to_char(self) -> chr:
            return chr(self.value + 65)

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
        self.observing: bool = bool(observing)
        if type(delay) is Delay:
            self.delay: Delay = delay
        else:
            self.delay: Delay = Delay(int(delay))
        self.critical_only: bool = bool(critical_only)
        self.stage: Stage = stage
        self.sub_stage: Stage = sub_stage

    @staticmethod
    def init(user: User) -> 'Admin':
        return Admin(
            aid=user.id,
            username=user.username
        )


class Service(BaseModel):
    class KeysId(int, EnumTool):
        sid = 0
        name = 1
        link = 2
        is_additional = 3

    def __init__(
            self,
            sid: int = -1,
            name: str = "",
            link: str = "",
            is_additional: bool = False
    ):
        self.sid: int = int(sid)
        self.name: str = name
        self.link: str = link
        self.is_additional: bool = bool(is_additional)


class Report(BaseModel):
    class KeysId(int, EnumTool):
        rid = 0
        sid = 1
        service_id = 2
        status = 3
        duration = 4
        additional = 5
        date_time = 6

    def __init__(
            self,
            rid: int = -1,
            sid: int = -1,
            service_id: int = -1,
            status: int = -1,
            duration: int = -1,
            additional: str = "",
            date_time: Optional[datetime] = None
    ):
        self.rid: int = int(rid)
        self.sid: int = int(sid)
        self.service_id: int = int(service_id)
        self.status: int = int(status)
        self.duration: int = int(duration)
        self.additional: str = additional
        self.date_time: Optional[datetime] = date_time


class CallbackModel(BaseModel):
    def __init__(self, message: Optional[MessageKeys] = None, admin: Optional[Admin] = None):
        self.message: Optional[MessageKeys] = message
        self.admin = admin

    def encode(self) -> str:
        return f"{self.message} {self.admin.aid}"

    @staticmethod
    def decode(string: str) -> 'CallbackModel':
        args = string.split()
        if len(args) == 2:
            return CallbackModel(MessageKeys(args[0]), Admin(aid=int(args[1])))
        elif len(args) == 1:
            return CallbackModel(MessageKeys(args[0]))
        else:
            return CallbackModel()

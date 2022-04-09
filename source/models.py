from datetime import datetime
from telegram import User
from typing import Optional
from constants import Delay, Stage


class Admin:
    def __init__(self):
        self.id: int = -1
        self.tg_user: Optional[User] = None
        self.token: str = ""
        self.observing: bool = False
        self.delay: Delay = Delay.one
        self.critical_only: bool = False
        self.stage: Stage = Stage.HELLO
        self.sub_stage: Stage = Stage.HELLO


class Service:
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

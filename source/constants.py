from enum import Enum
import os


SUPER_ADMIN_ID = 247427744
BOT_API_KEY = os.getenv("BOT_API_KEY")
BOT_STATE = os.getenv("BOT_STATE")

LOGS_DB_NAME = 'Logs'
DATABASE_NAME = 'Database'


class Delay(int, Enum):
    quarter = 15
    half = 30
    one = 60
    six = 360
    day = 1440


class Command(str, Enum):
    start = "start"
    start_observe = "start_observe"
    stop_observe = "stop_observe"
    add_service = "add_service"
    select_service = "select_service"
    change_delay = "change_delay"
    start_audit = "start_audit"
    stop_audit = "stop_audit"


class Stage(str, Enum):
    HELLO = "HELLO"
    LOGIN = "LOGIN"
    PASSWORD = "PASSWORD"
    ACCESS_CHECKING = "ACCESS_CHECKING"

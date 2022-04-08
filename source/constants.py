from enum import Enum


class Delay(Enum):
    quarter = 15
    half = 30
    one = 60
    six = 360
    day = 1440


class Command(Enum):
    start = "/start"
    start_observe = "/start_observe"
    stop_observe = "/stop_observe"
    add_service = "/add_service"
    select_service = "/select_service"
    change_delay = "/change_delay"

import ast
from enum import Enum
from typing import Optional

from telegram import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup
import os


# ---------------------------------------------------------------------------------------
# Text Manager

class TextManager:
    shared: 'TextManager' = None
    texts_url = os.path.join(os.path.dirname(__file__), 'texts.json')

    class Keys(Enum):
        EXAMPLE_KEY = "EXAMPLE_KEY"
        HELLO = "HELLO"
        HOME = "HOME"
        CHECKING_ACCESS = "CHECKING_ACCESS"
        ENTER_LOGIN = "ENTER_LOGIN"
        LOGIN_RECEIVED = "LOGIN_RECEIVED"
        ENTER_PASS = "ENTER_PASS"
        PASS_RECEIVED = "PASS_RECEIVED"
        CHECKING = "CHECKING"
        TRY_AGAIN_LOGIN = "TRY_AGAIN_LOGIN"
        SUCCESS_AUTH = "SUCCESS_AUTH"
        USER_NOT_FOUND = "USER_NOT_FOUND"
        SUCCESS = "SUCCESS"
        TRY_AGAIN = "TRY_AGAIN"
        SOMETHING_WRONG = "SOMETHING_WRONG"
        UNSUCCES_USER = "UNSUCCES_USER"

    def __new__(cls):
        if cls.shared is None:
            cls.shared: TextManager = super(TextManager, cls).__new__(cls)
        return cls.shared

    def __init__(self):
        self.texts: {str: str} = {}
        self.get_storage()

    def get_storage(self):
        self.texts = self.extract_file(f_url=TextManager.texts_url)

    @staticmethod
    def extract_file(f_url: str) -> dict:
        f = open(f_url, "r")
        text = f.read()
        f.close()
        return ast.literal_eval(text)

    def text_by_key(self, key: Keys) -> Optional[str]:
        self.get_storage()  # Here is auto update of storage
        return self.texts[key.value]


# ---------------------------------------------------------------------------------------
# Statuses

def success_auth() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.SUCCESS_AUTH)


def user_not_found() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.USER_NOT_FOUND)


def login_or_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=TextManager.shared.text_by_key(TextManager.Keys.TRY_AGAIN_LOGIN),
                                     callback_data=str(TextManager.Keys.TRY_AGAIN_LOGIN.value))
            ],
            [
                home_button()
            ]
        ]
    )


# ---------------------------------------------------------------------------------------
# Hello

def start() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.HELLO)


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=TextManager.shared.text_by_key(TextManager.Keys.FIND_CAR_BT),
                                     callback_data=str(TextManager.Keys.FIND_CAR_BT.value))
            ],
            [
                InlineKeyboardButton(text=TextManager.shared.text_by_key(TextManager.Keys.I_DRIVER_BT),
                                     callback_data=str(TextManager.Keys.I_DRIVER_BT.value))
            ]
        ]
    )


def home_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=TextManager.shared.text_by_key(TextManager.Keys.HOME),
        callback_data=str(TextManager.Keys.HOME.value)
    )


def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        home_button()
    ]])


def in_progress() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.CHECKING)


def some_wrong() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.SOMETHING_WRONG)


def success() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.SUCCESS)


# ---------------------------------------------------------------------------------------
# Login

def checking_access() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.CHECKING_ACCESS)


def enter_login() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.ENTER_LOGIN)


def login_received() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.LOGIN_RECEIVED)


def enter_password() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.ENTER_PASS)


def password_received() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.PASS_RECEIVED)


def get_user_error() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.UNSUCCES_USER)


# ---------------------------------------------------------------------------------------
# Search car


def car_info() -> str:
    print(TextManager.shared)
    return TextManager.shared.text_by_key(TextManager.Keys.CAR_INFO)


def enter_car_code_to_find() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.ENTER_CAR_CODE_FIND)


def car_not_found() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.CAR_NOT_FOUND)


def update_car_info_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=TextManager.shared.text_by_key(TextManager.Keys.UPDATE_INFO),
                                     callback_data=str(TextManager.Keys.UPDATE_INFO.value))
            ],
            [
                home_button()
            ]
        ]
    )


# ---------------------------------------------------------------------------------------
# I driver car

def enter_self_car_code() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.ENTER_CAR_CODE_SELF)


def driver_instruction() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.INSTRUCTION)


def driver_instruction_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text=TextManager.shared.text_by_key(TextManager.Keys.START),
                                     callback_data=str(TextManager.Keys.START.value))
            ],
            [
                home_button()
            ]
        ]
    )


def ask_location() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.ASK_SHARE_LOCATION)


def location_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=TextManager.shared.text_by_key(TextManager.Keys.SHARE_LOCATION),
                               request_location=True)
            ]
        ],
        resize_keyboard=True
    )


def try_again() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.TRY_AGAIN)


def timer_is_set() -> str:
    return TextManager.shared.text_by_key(TextManager.Keys.TIMER_IS_SET)


# ---------------------------------------------------------------------------------------
# Example

def ask_phone_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text=TextManager.shared.text_by_key(TextManager.Keys.EXAMPLE_KEY),
                               request_contact=True)
            ]
        ],
        resize_keyboard=True
    )
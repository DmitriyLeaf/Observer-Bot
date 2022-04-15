import os
import ast
from enum import Enum
from typing import Optional

from models import Admin, CallbackModel
from constants import MessageKeys

from telegram import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardMarkup


# ---------------------------------------------------------------------------------------
# Text Manager


class TextManager:
    shared: 'TextManager' = None
    texts_url = os.path.join(os.path.dirname(__file__), 'texts.json')

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

    def text_by_key(self, key: MessageKeys) -> Optional[str]:
        self.get_storage()  # Here is auto update of storage
        return self.texts[key.value]


# ---------------------------------------------------------------------------------------
# Access

def request_access(admin: Admin) -> str:
    return TextManager.shared.text_by_key(MessageKeys.ACCESS_REQUEST).format(
        admin.aid,
        admin.username
    )


def admin_access_keyboard(admin: Admin) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=TextManager.shared.text_by_key(MessageKeys.GRANT_ACCESS),
                    callback_data=CallbackModel(
                        message=MessageKeys.GRANT_ACCESS,
                        admin=admin
                    ).encode()
                )
            ],
            [
                InlineKeyboardButton(
                    text=TextManager.shared.text_by_key(MessageKeys.DENY_ACCESS),
                    callback_data=CallbackModel(
                        message=MessageKeys.DENY_ACCESS,
                        admin=admin
                    ).encode()
                )
            ]
        ]
    )


def access_is_checking() -> str:
    return TextManager.shared.text_by_key(MessageKeys.ACCESS_IS_CHECKING)


def access_request_sent() -> str:
    return TextManager.shared.text_by_key(MessageKeys.ACCESS_REQUEST_SENT)


def access_granted() -> str:
    return TextManager.shared.text_by_key(MessageKeys.ACCESS_GRANTED)


def in_development() -> str:
    return TextManager.shared.text_by_key(MessageKeys.IN_DEVELOPMENT)


# ---------------------------------------------------------------------------------------
# Home

def home() -> str:
    return TextManager.shared.text_by_key(MessageKeys.HOME)


def home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(text=TextManager.shared.text_by_key(case), callback_data=str(case.value))]
            for case in MessageKeys.home_cases()
        ]
    )


def home_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=TextManager.shared.text_by_key(MessageKeys.HOME_BUTTON),
        callback_data=str(MessageKeys.HOME_BUTTON.value)
    )


def go_home_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                home_button()
            ]
        ]
    )

import os
import time
from enum import Enum
from logging import Logger
from typing import Optional

import messages as msg
from constants import Command, SUPER_ADMIN_ID, LOGS_DB_NAME, DATABASE_NAME
from models import Admin
from constants import Stage
from tools import DateTime as DT_tool

import gspread
from gspread import Spreadsheet, Worksheet, Client, WorksheetNotFound

from telegram.ext.utils.promise import Promise
from telegram import User, Bot, ParseMode
from telegram.ext import Dispatcher


# ---------------------------------------------------------------------------------------
# TempSession

class TempSession:
    shared: "TempSession" = None

    def __new__(cls):
        if cls.shared is None:
            cls.shared: TempSession = super(TempSession, cls).__new__(cls)
        return cls.shared

    def __init__(self):
        self.sessions: {str: Admin} = {}

    def get_admin(self, user: Optional[User], bot: Optional[Bot] = None) -> Optional[Admin]:
        if user.id in self.sessions:
            l_user = self.sessions[user.id]
            return l_user
        elif bot is not None:
            bot.send_message(
                chat_id=user.id,
                text=msg.get_user_error()
            )
        return None

    def get_user_or_create(self, user: User) -> Admin:
        if user.id in self.sessions:
            l_user = self.sessions[user.id]
            l_user.add_new_login()
            return l_user
        else:
            return self.append_new_user(user)

    def append_new_user(self, user: User) -> Admin:
        new_user = Admin()
        self.sessions[user.id] = new_user
        return new_user

    def set_stage_for(self, user: User, stage: Stage):
        if self.get_admin(user=user) is not None:
            cuser = self.get_admin(user=user)
            cuser.stage = stage

    def set_sub_stage_for(self, user: User, sub_stage: Stage):
        if self.get_admin(user=user) is not None:
            cuser = self.get_admin(user=user)
            cuser.sub_stage = sub_stage


# ---------------------------------------------------------------------------------------
# BotDebugger

class BotDebugger:
    shared: "BotDebugger" = None

    def __new__(cls, dispatcher: Dispatcher, logger:  Logger):
        if cls.shared is None:
            cls.shared: BotDebugger = super(BotDebugger, cls).__new__(cls)
        return cls.shared

    def __init__(self, dispatcher: Dispatcher, logger:  Logger):
        self.bot: Optional[Bot] = None
        self.is_audition: bool = False
        self.audition_promise: Optional[Promise] = None
        self.start_time = DT_tool.now()
        self.dispatcher: Dispatcher = dispatcher
        self.logger: Logger = logger

        DBManager(dispatcher)

    def start_bot_audition(self, bot: Bot, dispatcher: Dispatcher):
        if self.is_audition:
            self.ping_to_admin()
            return
        self.bot = bot
        self.dispatcher = dispatcher
        self.is_audition = True
        self.audition_promise = self.dispatcher.run_async(self.audition_thread)

    def audition_thread(self):
        while self.is_audition:
            self.ping_to_admin()
            time.sleep(60*60)

    def ping_to_admin(self):
        self.bot.send_message(
            chat_id=SUPER_ADMIN_ID,
            text=f"<b>Ping 🏓</b> \n\n👥 Sessions: {len(TempSession.shared.sessions)} \n\n"
                 f"🔵 Current time:\n<code>{DT_tool.now()}</code> \n"
                 f"🟢 Start time:\n<code>{self.start_time}</code> \n\n"
                 f"/{Command.start_audit.value}\n/{Command.stop_audit.value}",
            parse_mode=ParseMode.HTML,
            disable_notification=True
        )

    def stop_bot_audition(self):
        self.ping_to_admin()
        self.bot.send_message(
            chat_id=SUPER_ADMIN_ID,
            text="Audition <b>STOPPED</b> 🛑",
            parse_mode=ParseMode.HTML
        )
        self.is_audition = False

    def info_log(self, admin: Admin, title: str = "INFO", text: str = ""):
        message = f"\n=== {title}: {text} \n[ {admin.tg_user.id}, {admin.tg_user.username} ] " \
                  f"[ {admin.stage}, {admin.sub_stage} ]\n"
        self.logger.info(msg=message)
        message = f"{DT_tool.now()} - INFO - {message}"
        DBManager.shared.write_to_logs(message)

    def info_log_simple(self, title: str = "INFO", text: str = ""):
        message = f"{title}: {text}"
        self.logger.info(msg=message)
        message = f"{DT_tool.now()} - INFO - {message}"
        DBManager.shared.write_to_logs(message)

    def error_log_simple(self, title: str = "INFO", text: str = ""):
        message = f"{title}: {text}"
        self.logger.error(msg=message)
        message = f"{DT_tool.now()} - ERROR - {message}"
        DBManager.shared.write_to_logs(message)


# ---------------------------------------------------------------------------------------
# DBManager

class DBManager:
    shared: 'DBManager' = None

    class DBKeys(Enum):
        ADMINS = "ADMINS"
        SERVICES = "SERVICES"
        REPORTS = "REPORTS"

        @staticmethod
        def cases() -> ['DBManager.DBKeys']:
            return list(map(lambda c: c, DBManager.DBKeys))

        @staticmethod
        def values() -> [str]:
            return list(map(lambda c: c.value, DBManager.DBKeys))

    def __new__(cls, dispatcher: Dispatcher):
        if cls.shared is None:
            cls.shared: DBManager = super(DBManager, cls).__new__(cls)
        return cls.shared

    def __init__(self, dispatcher: Dispatcher):
        self.dispatcher: Dispatcher = dispatcher

        self.gc: Optional[Client] = None

        self.logs_queue: set = set()
        self.logs_spreadsheet: Optional[Spreadsheet] = None
        self.logs_sheet: Optional[Worksheet] = None

        self.database_spreadsheet: Optional[Spreadsheet] = None
        self.database_sheets: {DBManager: Optional[Worksheet]} = {}
        self.is_database_syncing: bool = False

        self.dispatcher.run_async(self.authorize_open_spreadsheet)

    def authorize_open_spreadsheet(self):
        s_path = os.path.join(os.path.dirname(__file__), 'secrets/watchful-branch-311311-ed09b37b7304.json')
        self.gc = gspread.service_account(s_path)
        self.logs_spreadsheet = self.gc.open(LOGS_DB_NAME)
        self.database_spreadsheet = self.gc.open(DATABASE_NAME)
        BotDebugger.shared.info_log_simple(
            title="DB MANAGER",
            text="Success authorize and open spreadsheet"
        )
        self.get_log_sheet()
        self.get_database_sheets()

    def get_log_sheet(self):
        try:
            self.logs_sheet = self.logs_spreadsheet.worksheet(self.logs_worksheet_title())
            BotDebugger.shared.info_log_simple(
                title="DB MANAGER",
                text=f"Success LOG worksheet by title: {self.logs_worksheet_title()}"
            )
        except WorksheetNotFound:
            self.logs_sheet = self.logs_spreadsheet.add_worksheet(self.logs_worksheet_title(), rows=5, cols=5, index=0)
            BotDebugger.shared.info_log_simple(
                title="DB MANAGER",
                text=f"Success add LOG worksheet by title: {self.logs_worksheet_title()}"
            )
        finally:
            self.__write_logs_queue()

    def get_database_sheets(self):
        if self.is_database_syncing:
            return
        self.is_database_syncing = True
        for sheet_case in self.DBKeys.cases():
            self.get_db_sheet_by(case=sheet_case)
        self.is_database_syncing = False

    def get_db_sheet_by(self, case: 'DBManager.DBKeys'):
        try:
            sheet = self.database_spreadsheet.worksheet(case.value)
            BotDebugger.shared.info_log_simple(
                title="DB MANAGER",
                text=f"Success worksheet by title: {case.value}"
            )
            self.database_sheets[case] = sheet
        except WorksheetNotFound:
            sheet = self.database_spreadsheet.add_worksheet(case.value, rows=5, cols=5, index=0)
            BotDebugger.shared.info_log_simple(
                title="DB MANAGER",
                text=f"Success add worksheet by title: {case.value}"
            )
            self.database_sheets[case] = sheet

    @staticmethod
    def logs_worksheet_title():
        return str(DT_tool.now_day())

    def write_to_logs(self, message: str):
        self.dispatcher.run_async(self.__write_to_logs, message)

    def __write_to_logs(self, message: str):
        if self.logs_sheet is None:
            self.logs_queue.add(message)
            return
        if self.logs_sheet.title != self.logs_worksheet_title():
            self.logs_queue.add(message)
            self.get_log_sheet()
            return
        self.logs_sheet.insert_rows(values=[[message]], row=1)

    def __write_logs_queue(self):
        if self.logs_sheet is None:
            return
        for message in self.logs_queue:
            self.__write_to_logs(message)
        self.logs_queue = set()

import os
import time
import json
from enum import Enum
from logging import Logger
from typing import Optional

import messages as msg
from constants import *
from models import Admin
from constants import Stage
from tools import DateTime as DT_tool, EnumTool

import gspread
from gspread import Spreadsheet, Worksheet, Client, WorksheetNotFound, Cell

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

    def get_admin(self, user: Optional[User]) -> Optional[Admin]:
        if user.id in self.sessions:
            l_user = self.sessions[user.id]
            return l_user
        return None

    def get_user_or_create(self, user: User) -> Admin:
        if user.id in self.sessions:
            l_user = self.sessions[user.id]
            return l_user
        else:
            return self.append_new_user(user)

    def append_new_user(self, user: User) -> Admin:
        admin = Admin.init(user)
        self.sessions[admin.aid] = admin
        return admin

    def set_stage_for(self, user: User, stage: Stage):
        admin = self.get_admin(user=user)
        if admin is not None:
            admin.stage = stage

    def set_sub_stage_for(self, user: User, sub_stage: Stage):
        admin = self.get_admin(user=user)
        if admin is not None:
            admin.sub_stage = sub_stage


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
        self.delay: Delay = Delay.one

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
            time.sleep(self.delay.seconds_value())

    def ping_to_admin(self):
        self.bot.send_message(
            chat_id=SUPER_ADMIN_ID,
            text=f"<b>Ping 🏓</b> \n\n👥 Sessions: {len(TempSession.shared.sessions)} \n\n"
                 f"{DBManager.shared.get_db_status_str()}\n\n"
                 f"🔵 Current time:\n<code>{DT_tool.now()}</code> \n"
                 f"⚪️ Start time:\n<code>{self.start_time}</code> \n\n"
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
        message = f"\n=== {title}: {text} \n[ {admin.aid}, {admin.username} ] " \
                  f"[ {admin.stage}, {admin.sub_stage} ]\n"
        self.logger.info(msg=message)
        message = f"{DT_tool.now()} - INFO - {message}"
        DBManager.shared.write_to_logs(message)

    def info_log_user(self, user: User, title: str = "INFO", text: str = ""):
        message = f"\n=== {title}: {text} \n[ {user.id}, {user.username} ] " \
                  f"[ {user.first_name}, {user.last_name} ]\n"
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

    class DBKeys(EnumTool):
        ADMINS = "ADMINS"
        SERVICES = "SERVICES"
        REPORTS = "REPORTS"

        def keys_list(self) -> list:
            if self == DBManager.DBKeys.ADMINS:
                return list(Admin().__dict__.keys())
            else:
                return list()

        def decorated(self):
            max_len = len(max(self.__class__.values(), key=len))
            diff = max_len - len(self.value)
            return self.value + (" "*diff)

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
        self.is_logs_OK: bool = False

        self.database_spreadsheet: Optional[Spreadsheet] = None
        self.database_sheets: {DBManager: Optional[Worksheet]} = {}
        self.is_database_syncing: bool = False
        self.is_database_OK: bool = False
        self.database_statuses: {DBManager.DBKeys: bool} = {}
        self.synced_data: {DBManager.DBKeys: list} = {}

        # self.dispatcher.run_async(self.authorize_open_spreadsheet)
        self.authorize_open_spreadsheet()

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
        self.sync_database_data()

    def get_database_sheets(self):
        if not self.can_start_db_sync():
            return

        for sheet_case in self.DBKeys.cases():
            self.get_db_sheet_by(case=sheet_case)

        self.stop_db_sync()

    def get_db_sheet_by(self, case: 'DBManager.DBKeys'):
        self.database_statuses[case] = False
        try:
            sheet = self.database_spreadsheet.worksheet(case.value)
            BotDebugger.shared.info_log_simple(
                title="DB MANAGER",
                text=f"Success worksheet by title: {case.value}"
            )
            self.database_sheets[case] = sheet
        except WorksheetNotFound:
            sheet = self.database_spreadsheet.add_worksheet(case.value, rows=1, cols=1, index=0)
            BotDebugger.shared.info_log_simple(
                title="DB MANAGER",
                text=f"Success add worksheet by title: {case.value}"
            )
            self.database_sheets[case] = sheet
            sheet.insert_rows(values=[case.keys_list()], row=1)
        self.database_statuses[case] = True

    def sync_database_data(self):
        if not self.can_start_db_sync():
            return

        self.synced_data[self.DBKeys.ADMINS] = self.get_admins()

        self.stop_db_sync()

    def can_start_db_sync(self) -> bool:
        if self.is_database_syncing:
            return False
        self.is_database_syncing = True
        self.is_database_OK = False
        return True

    def stop_db_sync(self):
        self.is_database_syncing = False
        self.is_database_OK = True

    def get_db_status_str(self) -> str:
        detailed = ""
        for case in DBManager.DBKeys:
            count = int_to_emoji(len(self.synced_data[case])) if case in self.synced_data else int_to_emoji(0)
            detailed += f"    {'🟢' if case in self.database_statuses and self.database_statuses[case] else '🔴'} " \
                        f"{case.decorated()} " \
                        f"{count} \n"
        return f"🗄 Database: \n<code>    {'🟡' if DBManager.shared.is_database_syncing else '🟢'} sync\n" \
               f"    {'🟢' if DBManager.shared.is_database_OK else '🔴'} OK\n" \
               f"    {'🟢' if self.is_logs_OK else '🔴'} LOGS\n" \
               f"{detailed}</code>"

    def save_admin(self, admin: Admin):
        ws: Worksheet = self.database_sheets[self.DBKeys.ADMINS]
        cell: Cell = ws.find(str(admin.aid), in_column=Admin.KeysId.aid)
        if cell is not None:
            ws.update(f'A{cell.row}:{cell.row}', [admin.to_list()])
        else:
            ws.insert_rows(values=[admin.to_list()], row=len(ws.col_values(1))+1)

    def get_admin(self, admin: Admin) -> Optional[Admin]:
        ws: Worksheet = self.database_sheets[self.DBKeys.ADMINS]
        cell: Cell = ws.find(str(admin.aid), in_column=Admin.KeysId.aid)
        if cell is None:
            return None
        values: list = ws.row_values(cell.row)
        # keys = Admin().__dict__.keys()
        # a_dict = dict(zip(keys, values))
        try:
            adm = Admin.decode_list(values)
            return adm
        except:
            print("ERR")
            return None

    def get_admins(self) -> [Admin]:
        self.database_statuses[self.DBKeys.ADMINS] = False

        ws: Worksheet = self.database_sheets[self.DBKeys.ADMINS]
        end_coll_letter = Admin.KeysId.last().to_char()
        end_row_num = len(ws.col_values(1))
        ranges = [f'A2:{end_coll_letter}{end_row_num}']
        # print(ranges)
        rows = ws.batch_get(ranges)[0]
        self.database_statuses[self.DBKeys.ADMINS] = True
        # print(rows)
        return [Admin.decode_list(row) for row in rows]
        # print(admins)
        # [print(admin.to_dict()) for admin in admins]

    # ---------------------------------------------------------------------------------------
    # LOGS

    def get_log_sheet(self):
        self.is_logs_OK = False
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
            self.is_logs_OK = True
            self.__write_logs_queue()

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


def int_to_emoji(num) -> str:
    e_list = {'0': '0️⃣', '1': '1️⃣', '2': '2️⃣', '3': '3️⃣', '4': '4️⃣',
              '5': '5️⃣', '6': '6️⃣', '7': '7️⃣', '8': '8️⃣', '9': '9️⃣'}
    return ''.join([e_list[k] for k in str(num)])

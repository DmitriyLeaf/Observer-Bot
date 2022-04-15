import logging
import time
from typing import Optional

from models import Admin, CallbackModel
import messages as msg
import constants as const
from constants import Stage
from controllers import TempSession, BotDebugger, DBManager

from telegram import Update, ParseMode, ReplyKeyboardRemove, Bot, Message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, \
    Dispatcher

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued"""
    BotDebugger.shared.info_log_user(
        user=update.effective_user,
        title="BUTTON ACTION",
        text=update.message.text if update.message is not None else "callback"
    )

    user_session: Admin = get_admin(update, context)

    if user_session is None:
        return

    context.bot.send_message(
        chat_id=user_session.aid,
        text=msg.home(),
        reply_markup=msg.home_keyboard()
    )

    # DBManager.shared.save_admin(admin)
    # result = DBManager.shared.get_admin(admin)
    # print("R:", result)
    # print("R:", result.to_dict())
    # result = DBManager.shared.get_admins()


def buttons_action(update: Update, context: CallbackContext):
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    query.answer(query.data)
    callback: CallbackModel = CallbackModel.decode(query.data)

    BotDebugger.shared.info_log_user(
        user=update.effective_user,
        title="BUTTON ACTION",
        text=callback.message.value
    )

    user_session: Admin = get_admin(update, context)
    if user_session is None:
        return

    if callback.message == const.MessageKeys.GRANT_ACCESS:
        admin = TempSession.shared.get_admin_by(callback.admin.aid)
        grant_access(update, context, admin)
    elif callback.message == const.MessageKeys.DENY_ACCESS:
        admin = TempSession.shared.get_admin_by(callback.admin.aid)
        deny_access(update, context, admin)
    elif callback.message == const.MessageKeys.HOME_BUTTON:
        start(update, context)


def grant_access(update: Update, context: CallbackContext, admin: Optional[Admin] = None):
    if admin is None:
        return
    admin.token = "✅️"
    DBManager.shared.save_admin(admin)
    context.bot.send_message(
        chat_id=admin.aid,
        text=msg.access_granted(),
        parse_mode=ParseMode.HTML,
        reply_markup=msg.go_home_keyboard()
    )


def deny_access(update: Update, context: CallbackContext, admin: Optional[Admin] = None):
    if admin is None:
        return
    admin.token = ""
    DBManager.shared.save_admin(admin)


def start_observe(update: Update, context: CallbackContext):
    """Send a message when the command /start_observe is issued"""
    in_development(update, context)


def stop_observe(update: Update, context: CallbackContext):
    """Send a message when the command /stop_observe is issued"""
    in_development(update, context)


def add_service(update: Update, context: CallbackContext):
    """Send a message when the command /add_service is issued"""
    in_development(update, context)


def select_service(update: Update, context: CallbackContext):
    """Send a message when the command /select_service is issued"""
    in_development(update, context)


def change_delay(update: Update, context: CallbackContext):
    """Send a message when the command /change_delay is issued"""
    in_development(update, context)


def in_development(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=msg.in_development()
    )


def get_admin(update: Update, context: CallbackContext) -> Optional[Admin]:
    admin = TempSession.shared.get_admin(update.effective_user)
    if admin and len(admin.token) > 0:
        return admin
    elif admin and admin.stage == Stage.WAITING_ACCESS:
        context.bot.send_message(
            chat_id=admin.aid,
            text=msg.access_is_checking(),
        )
        return None
    else:
        admin = TempSession.shared.append_new_user(update.effective_user)
        admin.stage = Stage.WAITING_ACCESS
        context.bot.send_message(
            chat_id=const.SUPER_ADMIN_ID,
            text=msg.request_access(admin),
            reply_markup=msg.admin_access_keyboard(admin),
            parse_mode=ParseMode.HTML
        )
        context.bot.send_message(
            chat_id=admin.aid,
            text=msg.access_request_sent(),
            parse_mode=ParseMode.HTML
        )
        return None


def stop_audit(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /stop_audit is issued"""
    user = update.effective_user
    # user_session: Admin = TempSession.shared.get_user_or_create(user=update.effective_user)
    # BotDebugger.shared.info_log(
    #     c_user=user_session,
    #     title="STOP AUDIT",
    #     text=update.message.text
    # )
    if user.id == const.SUPER_ADMIN_ID:
        BotDebugger.shared.stop_bot_audition()


def start_audit(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start_audit is issued"""
    user = update.effective_user
    # user_session: CUser = TempSession.shared.get_user_or_create(user=update.effective_user)
    # BotDebugger.shared.info_log(
    #     c_user=user_session,
    #     title="START AUDIT",
    #     text=update.message.text
    # )
    if user.id == const.SUPER_ADMIN_ID:
        BotDebugger.shared.start_bot_audition(context.bot, context.dispatcher)


# ---------------------------------------------------------------------------------------
# Main

is_launching = False


def start_launching_process(bot: Bot, dispatcher: Dispatcher):
    process_message = bot.send_message(
        chat_id=const.SUPER_ADMIN_ID,
        text="Bot is setting up ⏳️"
    )
    global is_launching
    is_launching = True
    dispatcher.run_async(next_launching, process_message)


def next_launching(process_message: Message, switch: bool = True):
    time.sleep(0.3)
    if not is_launching:
        process_message.edit_text(
            text="Launch success ✅️"
        )
        return
    if switch:
        process_message.edit_text(
            text="Bot is setting up ⌛️"
        )
    else:
        process_message.edit_text(
            text="Bot is setting up ⏳️️"
        )
    switch = not switch
    next_launching(process_message, switch)


def stop_launching_process():
    global is_launching
    is_launching = False


def main():
    """Start the bot."""
    updater = Updater(const.BOT_API_KEY)
    dispatcher = updater.dispatcher

    # Start the Bot
    updater.start_polling()

    start_launching_process(updater.bot, dispatcher)

    # Init instances
    TempSession()
    msg.TextManager()
    BotDebugger(dispatcher, logger)
    DBManager(dispatcher)
    BotDebugger.shared.start_bot_audition(updater.bot, updater.dispatcher)

    dispatcher.add_handler(CommandHandler(const.Command.start.value, start))
    dispatcher.add_handler(CommandHandler(const.Command.start_audit.value, start_audit))
    dispatcher.add_handler(CommandHandler(const.Command.stop_audit.value, stop_audit))
    dispatcher.add_handler(CommandHandler(const.Command.start_observe.value, start_observe))
    dispatcher.add_handler(CommandHandler(const.Command.stop_observe.value, stop_observe))
    dispatcher.add_handler(CommandHandler(const.Command.add_service.value, add_service))
    dispatcher.add_handler(CommandHandler(const.Command.select_service.value, select_service))
    dispatcher.add_handler(CommandHandler(const.Command.change_delay.value, change_delay))
    dispatcher.add_handler(CallbackQueryHandler(buttons_action))

    stop_launching_process()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

import logging
import messages as msg
import constants as const

from models import Admin
from controllers import TempSession, BotDebugger

from telegram import Update, ParseMode, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
    CallbackQueryHandler,
)


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued"""
    user = update.effective_user
    user_session: Admin = TempSession.shared.get_user_or_create(user=user)
    admin = Admin(tg_user=user)
    print(admin.to_dict())
    print(admin.to_json())

    print(admin.tg_user.to_dict())
    print(admin.tg_user.to_json())
    BotDebugger.shared.info_log(
        admin=admin,
        title="NEW SESSION",
        text=update.message.text
    )


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


def main():
    """Start the bot."""
    updater = Updater(const.BOT_API_KEY)

    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler(const.Command.start.value, start))
    dispatcher.add_handler(CommandHandler(const.Command.start_audit.value, start_audit))
    dispatcher.add_handler(CommandHandler(const.Command.stop_audit.value, stop_audit))
    # dispatcher.add_handler(CommandHandler(const.Command.sos.value, sos))
    # dispatcher.add_handler(CallbackQueryHandler(buttons_action))

    # Init instances
    TempSession()
    msg.TextManager()
    BotDebugger(dispatcher, logger)
    BotDebugger.shared.start_bot_audition(updater.bot, updater.dispatcher)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

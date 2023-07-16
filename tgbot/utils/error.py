import logging
import traceback
import html

import telegram
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from dtb.settings import TELEGRAM_LOGS_CHAT_ID
from users.models import User

from text_manager.models import texts


def send_stacktrace_to_tg_chat(update: Update, context: CallbackContext) -> None:
    if isinstance(context.error, telegram.error.Unauthorized):
        return

    if isinstance(context.error, telegram.error.BadRequest) and context.error.message == "Chat not found":
        return

    logging.error("Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = "".join(tb_list)

    message = f"An exception was raised while handling an update\n" f"```{html.escape(tb_string)}```"

    if update:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=texts.user_error_message,
            parse_mode=ParseMode.HTML,
        )

        admin_message = f"⚠️⚠️⚠️ for {update.effective_chat.id}:\n{message}"[:4090]
    else:
        admin_message = f"⚠️⚠️⚠️ :\n{message}"[:4090]

    if TELEGRAM_LOGS_CHAT_ID:
        context.bot.send_message(
            chat_id=TELEGRAM_LOGS_CHAT_ID,
            text=admin_message,
            parse_mode=ParseMode.HTML,
        )
    else:
        logging.error(admin_message)

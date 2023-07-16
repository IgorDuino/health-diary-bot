from telegram.ext import (
    Dispatcher,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    PicklePersistence,
)

from dtb.settings import DEBUG

from tgbot.utils import files, error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.main import bot

from tgbot import states

from text_manager.models import button_texts


def s(pattern):
    def check(string):
        return string.startswith(pattern)

    return check


def setup_dispatcher(dp: Dispatcher):
    persistence = PicklePersistence(filename="conversations")
    dp.persistence = persistence

    dp.add_handler(CommandHandler("admin", admin_handlers.admin))

    dp.add_handler(CommandHandler("start", onboarding_handlers.start))
    dp.add_handler(MessageHandler(Filters.regex(button_texts.home), onboarding_handlers.start, pass_user_data=True))

    dp.add_handler(
        MessageHandler(Filters.regex(button_texts.statistics), onboarding_handlers.statistics, pass_user_data=True)
    )
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.statistics, pattern=s("previous_day"), pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.statistics, pattern=s("next_day"), pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.statistics, pattern=s("current_day"), pass_user_data=True))

    dp.add_handler(
        MessageHandler(Filters.regex(button_texts.addtionals), onboarding_handlers.addtional, pass_user_data=True)
    )

    add_garmin_conversation = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(button_texts.add_garmin), onboarding_handlers.add_garmin)],
        states={
            states.GARMIN_USERNAME: [
                MessageHandler(Filters.text, onboarding_handlers.garmin_username_handler, pass_user_data=True),
            ],
            states.GARMIN_PASSWORD: [
                MessageHandler(Filters.text, onboarding_handlers.garmin_password_handler, pass_user_data=True),
            ],
        },
        fallbacks=[MessageHandler(Filters.regex(button_texts.home), onboarding_handlers.start, pass_user_data=True)],
        name="add_garmin",
        persistent=True,
        per_user=True,
    )
    dp.add_handler(add_garmin_conversation)

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    return dp


n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))

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

from tgbot.utils import error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.main import bot

from tgbot import states

from text_manager.models import button_texts


def s(pattern) -> callable:
    def check(string):
        return string.startswith(pattern)

    return check


def setup_dispatcher(dp: Dispatcher):
    persistence = PicklePersistence(filename="conversations")
    dp.persistence = persistence

    fb = [
        CommandHandler("start", onboarding_handlers.start, pass_user_data=True),
        CallbackQueryHandler(onboarding_handlers.start, pattern=s("cancel"), pass_user_data=True),
    ]

    dp.add_handler(CommandHandler("admin", admin_handlers.admin))

    add_garmin_conversation = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex(button_texts.add_garmin), onboarding_handlers.add_garmin)],
        states={
            states.GARMIN_USERNAME: [
                MessageHandler(
                    Filters.text,
                    onboarding_handlers.garmin_username_handler,
                    pass_user_data=True,
                ),
            ],
            states.GARMIN_PASSWORD: [
                MessageHandler(
                    Filters.text,
                    onboarding_handlers.garmin_password_handler,
                    pass_user_data=True,
                ),
            ],
        },
        fallbacks=[
            *fb,
        ],
        name="add_garmin",
        persistent=True,
        per_user=True,
    )
    dp.add_handler(add_garmin_conversation)
    dp.add_handler(
        MessageHandler(
            Filters.regex(button_texts.home),
            onboarding_handlers.start,
            pass_user_data=True,
        )
    )

    dp.add_handler(
        MessageHandler(
            Filters.regex(button_texts.statistics),
            onboarding_handlers.statistics,
            pass_user_data=True,
        )
    )
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.statistics, pattern=s("previous_day"), pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.statistics, pattern=s("next_day"), pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.statistics, pattern=s("current_day"), pass_user_data=True))
    specify_date_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(onboarding_handlers.specify_date, pattern=s("specify_date"), pass_user_data=True)
        ],
        states={
            states.STAT_SPECIFY_DATE: [
                MessageHandler(
                    Filters.text,
                    onboarding_handlers.statistics_specify_date,
                    pass_user_data=True,
                ),
            ],
        },
        fallbacks=[
            *fb,
        ],
        name="specify_date",
        persistent=True,
        per_user=True,
    )
    dp.add_handler(specify_date_conversation)

    dp.add_handler(
        MessageHandler(
            Filters.regex(button_texts.addtionals),
            onboarding_handlers.addtional,
            pass_user_data=True,
        )
    )

    delete_meal_conversation = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(onboarding_handlers.delete_meal_start, pattern=s("delete_meal"), pass_user_data=True)
        ],
        states={
            states.DELETE_MEAL: [
                MessageHandler(
                    Filters.regex(r"^\d+$"),
                    onboarding_handlers.delete_meal,
                    pass_user_data=True,
                ),
            ],
        },
        fallbacks=[
            *fb,
        ],
        name="delete_meal",
        persistent=True,
        per_user=True,
    )
    dp.add_handler(delete_meal_conversation)

    add_meal_conversation = ConversationHandler(
        entry_points=[
            MessageHandler(~Filters.regex("^/start$"), onboarding_handlers.start_choose_meal, pass_user_data=True)
        ],
        states={
            states.CHOOSE_MEAL: [
                CallbackQueryHandler(
                    onboarding_handlers.choose_meal,
                    pattern=s("choose_meal:"),
                    pass_user_data=True,
                ),
            ],
            states.CHOOSE_MEAL_WEIGHT: [
                MessageHandler(
                    Filters.text,
                    onboarding_handlers.choose_meal_weight,
                    pass_user_data=True,
                ),
            ],
            states.CHOOSE_MEAL_DATE: [
                CallbackQueryHandler(
                    onboarding_handlers.choose_meal_date,
                    pattern=s("choose_meal_date:"),
                    pass_user_data=True,
                ),
                MessageHandler(
                    Filters.text,
                    onboarding_handlers.choose_meal_date,
                    pass_user_data=True,
                ),
            ],
        },
        fallbacks=[
            *fb,
        ],
        name="add_meal",
        persistent=True,
        per_user=True,
    )
    dp.add_handler(add_meal_conversation)

    for fallback in fb:
        dp.add_handler(fallback)

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    return dp


n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))

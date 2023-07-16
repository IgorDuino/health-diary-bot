from datetime import datetime, timedelta
import logging

from dtb import settings

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
from tgbot import states
import tgbot.handlers.onboarding.keyboards as keyboards

from text_manager.models import texts

from users.models import User

from diary.models import Dish, Meal

from tgbot.utils.garmin import check_garmin_credentials


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update)
    if user:
        created = False
    else:
        if settings.DISABLE_FOR_NEW_USERS:
            context.bot.send_message(
                chat_id=update.effective_user.id,
                text=texts.disabled_for_new_users,
                parse_mode=ParseMode.HTML,
            )
            return
        user = User(
            user_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
        )
        user.save()
        created = True

    if created:
        start_code = update.message.text.split(" ")[1] if len(update.message.text.split(" ")) > 1 else None
        if start_code:
            referrer = User.objects.filter(user_id=start_code).first()
            if referrer:
                user.deep_link = start_code

    if user.is_first_time:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=texts.start_first_time,
            reply_markup=keyboards.user_menu(user),
            parse_mode=ParseMode.HTML,
        )

        user.is_first_time = False

    user.is_active = True
    user.save()

    calories = 0
    protein = 0
    fats = 0
    carbohydrates = 0

    context.bot.send_message(
        chat_id=update.message.chat_id,
        text=texts.today_stat.format(
            calories=calories,
            protein=protein,
            fats=fats,
            carbohydrates=carbohydrates,
        ),
        reply_markup=keyboards.user_menu(user),
        parse_mode=ParseMode.HTML,
    )

    return ConversationHandler.END


def statistics(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update)

    date = context.user_data.get("date")
    if not date:
        date = datetime.now().date()
        context.user_data["date"] = date

    if update.callback_query:
        if update.callback_query.data.startswith("previous_day"):
            date -= timedelta(days=1)
        elif update.callback_query.data.startswith("next_day"):
            date += timedelta(days=1)
        elif update.callback_query.data.startswith("current_day"):
            date = datetime.now().date()

        context.user_data["date"] = date

    meals = Meal.objects.filter(user=user, created_at__date=date)

    total_calories = 0
    total_protein = 0
    total_fats = 0
    total_carbohydrates = 0

    products_text = ""

    for meal in meals:
        dish: Dish = meal.dish
        total_calories += dish.cal * meal.grams
        total_protein += dish.prot * meal.grams
        total_fats += dish.fat * meal.grams
        total_carbohydrates += dish.carb * meal.grams
        products_text += texts.product_stat.format(
            name=dish.title,
            grams=meal.grams,
            calories=dish.cal * meal.grams,
            protein=dish.prot * meal.grams,
            fats=dish.fat * meal.grams,
            carbohydrates=dish.carb * meal.grams,
        )

    text = texts.statistics.format(
        date=date,
        products=products_text,
        calories=total_calories,
        protein=total_protein,
        fats=total_fats,
        carbohydrates=total_carbohydrates,
    )

    if update.callback_query:
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboards.statistics_menu(),
            parse_mode=ParseMode.HTML,
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=text,
            reply_markup=keyboards.statistics_menu(),
            parse_mode=ParseMode.HTML,
        )


def addtional(update: Update, context: CallbackContext):
    user = User.get_user(update)

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.additional,
        reply_markup=keyboards.additional_menu(user),
        parse_mode=ParseMode.HTML,
    )


def add_garmin(update: Update, context: CallbackContext):
    user = User.get_user(update)

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.garmin_username,
        reply_markup=keyboards.home_menu(),
        parse_mode=ParseMode.HTML,
    )

    return states.GARMIN_USERNAME


def garmin_username_handler(update: Update, context: CallbackContext):
    user = User.get_user(update)

    context.user_data["garmin_username"] = update.message.text

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.garmin_password,
        reply_markup=keyboards.user_menu(user),
        parse_mode=ParseMode.HTML,
    )

    return states.GARMIN_PASSWORD


def garmin_password_handler(update: Update, context: CallbackContext):
    user = User.get_user(update)

    garmin_username = context.user_data.get("garmin_username")
    if not garmin_username:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=texts.user_error_message,
            reply_markup=keyboards.user_menu(user),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    garmin_password = update.message.text

    if not check_garmin_credentials(garmin_username, garmin_password):
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=texts.garmin_invalid_credentials,
            reply_markup=keyboards.home_menu(),
            parse_mode=ParseMode.HTML,
        )
        context.user_data["garmin_username"] = None

        return states.GARMIN_USERNAME

    user.garmin_login = garmin_username
    user.garmin_password = garmin_password
    user.save()

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.garmin_successfully_added,
        reply_markup=keyboards.user_menu(user),
        parse_mode=ParseMode.HTML,
    )

    return ConversationHandler.END

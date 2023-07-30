from datetime import datetime, timedelta
import logging

from dtb import settings

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
from tgbot import states
import tgbot.handlers.onboarding.keyboards as keyboards

from text_manager.models import texts, button_texts

from users.models import User

from diary.models import Dish, Meal
from fuzzywuzzy import process

from tgbot.utils.garmin import check_garmin_credentials


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
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
            chat_id=update.effective_user.id,
            text=texts.start_first_time,
            reply_markup=keyboards.user_menu(user),
            parse_mode=ParseMode.HTML,
        )

        user.is_first_time = False

    user.is_active = True
    user.save()

    meals = Meal.objects.filter(user=user, created_at__date=datetime.now().date())

    calories = 0
    protein = 0
    fats = 0
    carbohydrates = 0

    for meal in meals:
        dish: Dish = meal.dish
        calories += dish.cal * meal.grams
        protein += dish.prot * meal.grams
        fats += dish.fat * meal.grams
        carbohydrates += dish.carb * meal.grams

    text = texts.today_stat.format(
        calories=int(calories),
        protein=int(protein),
        fats=int(fats),
        carbohydrates=int(carbohydrates),
    )

    if update.callback_query:
        update.callback_query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=text,
            reply_markup=keyboards.user_menu(user),
            parse_mode=ParseMode.HTML,
        )

    context.user_data["dishes_to_handle"] = []

    return ConversationHandler.END


def specify_date(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text(
        text=texts.specify_date,
        reply_markup=keyboards.cancel_button(),
        parse_mode=ParseMode.HTML,
    )

    return states.STAT_SPECIFY_DATE


def statistics(update: Update, context: CallbackContext):
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

    elif update.message.text != button_texts.statistics:
        date = update.message.text
        try:
            date = datetime.strptime(date, "%d.%m.%y").date()
        except ValueError:
            context.bot.send_message(
                chat_id=update.effective_user.id,
                text=texts.specify_date,
                reply_markup=keyboards.cancel_button(),
                parse_mode=ParseMode.HTML,
            )
            return states.STAT_SPECIFY_DATE

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
            grams=int(meal.grams),
            calories=int(dish.cal * meal.grams),
            protein=int(dish.prot * meal.grams),
            fats=int(dish.fat * meal.grams),
            carbohydrates=int(dish.carb * meal.grams),
        )

    text = texts.statistics.format(
        date=date,
        products=products_text,
        calories=int(total_calories),
        protein=int(total_protein),
        fats=int(total_fats),
        carbohydrates=int(total_carbohydrates),
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

    return ConversationHandler.END


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
        reply_markup=keyboards.cancel_button(),
        parse_mode=ParseMode.HTML,
    )

    return states.GARMIN_USERNAME


def garmin_username_handler(update: Update, context: CallbackContext):
    user = User.get_user(update)

    context.user_data["garmin_username"] = update.message.text

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.garmin_password,
        reply_markup=keyboards.cancel_button(),
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
            reply_markup=keyboards.cancel_button(),
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


def start_choose_meal(update: Update, context: CallbackContext):
    user = User.get_user(update)

    if not (update.message and update.message.text) and len(context.user_data.get("dishes_to_handle", [])) == 0:
        update.callback_query.edit_message_text(
            text=texts.user_error_message,
            reply_markup=keyboards.call_menu(),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    if update.message and update.message.text:
        data = update.message.text.strip().splitlines()
        data = list(filter(lambda x: x, data))

    else:
        data = context.user_data["dishes_to_handle"]

    text = data[0]
    context.user_data["dishes_to_handle"] = data[1:]

    if text.split()[-1].isdigit():
        weight = int(text.split()[-1])
        text = " ".join(text.split()[:-1])
        context.user_data["weight"] = weight

    dishes = Dish.objects.all()

    top = process.extract(text, dishes, limit=8)

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.choose_meal.format(name=text),
        reply_markup=keyboards.choose_meal(top),
        parse_mode=ParseMode.HTML,
    )

    return states.CHOOSE_MEAL


def choose_meal(update: Update, context: CallbackContext):
    user = User.get_user(update)

    dish_id = update.callback_query.data.split(":")[1]

    dish = Dish.objects.get(id=dish_id)

    context.user_data["dish"] = dish

    update.callback_query.edit_message_text(
        text=texts.choose_meal_weight.format(title=dish.title),
        reply_markup=keyboards.cancel_button(),
        parse_mode=ParseMode.HTML,
    )

    if context.user_data.get("weight"):
        try:
            weight = int(context.user_data["weight"])
            return choose_meal_date(update, context)
        except ValueError:
            pass

    return states.CHOOSE_MEAL_WEIGHT


def choose_meal_weight(update: Update, context: CallbackContext):
    user = User.get_user(update)

    dish: Dish = context.user_data.get("dish")
    if not dish:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=texts.user_error_message,
            reply_markup=keyboards.cancel_button(),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    if not context.user_data.get("weight", None):
        weight = update.message.text
    else:
        weight = context.user_data["weight"]

    try:
        weight = int(weight)
    except ValueError:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=texts.choose_meal_weight.format(title=dish.title),
            reply_markup=keyboards.cancel_button(),
            parse_mode=ParseMode.HTML,
        )
        return states.CHOOSE_MEAL_WEIGHT

    context.user_data["weight"] = weight

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.choose_meal_date.format(title=dish.title, weight=weight),
        reply_markup=keyboards.choose_meal_date(),
        parse_mode=ParseMode.HTML,
    )

    return states.CHOOSE_MEAL_DATE


def choose_meal_date(update: Update, context: CallbackContext):
    user = User.get_user(update)

    dish: Dish = context.user_data.get("dish")
    weight: int = context.user_data.get("weight")

    if not dish or not weight:
        update.callback_query.edit_message_text(
            text=texts.user_error_message,
            reply_markup=keyboards.home_menu(),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    if update.callback_query:
        date = update.callback_query.data.split(":")[1]
    else:
        date = update.message.text

    try:
        if date == "today":
            date = datetime.now()
        elif date == "yesterday":
            date = datetime.now() - timedelta(days=1)
        elif date == "tommorow":
            date = datetime.now() + timedelta(days=1)
        else:
            date = datetime.strptime(date, "%d.%m.%y %H:%M")

    except ValueError as e:
        if update.callback_query:
            update.callback_query.edit_message_text(
                text=texts.choose_meal_date.format(title=dish.title, weight=weight),
                reply_markup=keyboards.choose_meal_date(),
                parse_mode=ParseMode.HTML,
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_user.id,
                text=texts.choose_meal_date.format(title=dish.title, weight=weight),
                reply_markup=keyboards.choose_meal_date(),
                parse_mode=ParseMode.HTML,
            )

        return states.CHOOSE_MEAL_DATE

    meal = Meal(user=user, dish=dish, grams=weight, created_at=date)
    meal.save()

    if update.callback_query:
        update.callback_query.edit_message_text(
            text=texts.meal_added.format(title=dish.title, weight=weight, date=date),
            parse_mode=ParseMode.HTML,
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=texts.meal_added.format(title=dish.title, weight=weight, date=date),
            reply_markup=keyboards.home_menu(),
            parse_mode=ParseMode.HTML,
        )

    dishes_to_handle = context.user_data.get("dishes_to_handle", [])
    context.user_data["weight"] = None

    if len(dishes_to_handle) == 0:
        return start(update, context)

    return start_choose_meal(update, context)

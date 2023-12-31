from datetime import datetime, timedelta
import logging
import re

from dtb import settings

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
from tgbot import states
import tgbot.handlers.onboarding.keyboards as keyboards

from text_manager.models import texts, button_texts

from users.models import User
from diary.models import Dish, Meal, GarminSyncedData

from fuzzywuzzy import process

from tgbot.utils.garmin import check_garmin_credentials
from tgbot.utils.aescrypto import encrypt_data


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

    meals = Meal.objects.filter(user=user, date_time__date=datetime.now().date())

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

    context.user_data.clear()

    return ConversationHandler.END


def specify_date(update: Update, context: CallbackContext):
    update.callback_query.edit_message_text(
        text=texts.specify_date,
        reply_markup=keyboards.cancel_button(),
        parse_mode=ParseMode.HTML,
    )

    return states.STAT_SPECIFY_DATE


def statistics_specify_date(update: Update, context: CallbackContext):
    text_date = update.message.text

    date_formats = [
        "%d.%m",
        "%d.%m.%y",
        "%d.%m.%Y",
    ]
    parsed_date = None
    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(text_date, date_format)
            if date_format == "%d.%m":
                parsed_date = parsed_date.replace(year=datetime.now().year)
            break
        except ValueError:
            pass
    else:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=texts.specify_date,
            reply_markup=keyboards.cancel_button(),
            parse_mode=ParseMode.HTML,
        )
        return states.STAT_SPECIFY_DATE

    context.user_data["date"] = parsed_date.date()

    return statistics(update, context)


def statistics(update: Update, context: CallbackContext):
    user = User.get_user(update)

    date = context.user_data.get("date", datetime.now().date())

    if update.callback_query:
        if update.callback_query.data.startswith("previous_day"):
            date -= timedelta(days=1)
        elif update.callback_query.data.startswith("next_day"):
            date += timedelta(days=1)
        elif update.callback_query.data.startswith("current_day"):
            date = datetime.now().date()

    context.user_data["date"] = date

    meals = Meal.objects.filter(user=user, date_time__date=date).order_by("date_time")

    total_calories = 0
    total_protein = 0
    total_fats = 0
    total_carbohydrates = 0

    products_text = ""

    prev_time = None

    for i, meal in enumerate(meals):
        dish: Dish = meal.dish
        total_calories += dish.cal * meal.grams
        total_protein += dish.prot * meal.grams
        total_fats += dish.fat * meal.grams
        total_carbohydrates += dish.carb * meal.grams

        if prev_time != meal.date_time:
            prev_time = meal.date_time
            tm = meal.date_time.strftime("%H:%M")
            products_text += f"<b>{tm}</b>\n"

        products_text += texts.product_stat.format(
            name=dish.title,
            grams=int(meal.grams),
            calories=int(dish.cal * meal.grams),
            protein=int(dish.prot * meal.grams),
            fats=int(dish.fat * meal.grams),
            carbohydrates=int(dish.carb * meal.grams),
        )

    garmin_stat_text = ""
    garmin_stat = GarminSyncedData.objects.filter(user=user, date_time__date=date).order_by("-date_time").first()
    if garmin_stat:
        garmin_stat_text = "\n\n" + texts.garmin_stat.format(
            body_battery_charged_value=garmin_stat.body_battery_charged_value,
            body_battery_drained_value=garmin_stat.body_battery_drained_value,
            body_battery_highest_value=garmin_stat.body_battery_highest_value,
            resting_heart_rate=garmin_stat.resting_heart_rate,
            max_avg_heart_rate=garmin_stat.max_avg_heart_rate,
            average_stress_level=garmin_stat.average_stress_level,
            hour_sleep=garmin_stat.minutes_sleep // 60,
            minutes_sleep=garmin_stat.minutes_sleep % 60,
            total_steps=garmin_stat.total_steps,
            lowest_respiration_value=garmin_stat.lowest_respiration_value,
            avg_waking_respiration_value=garmin_stat.avg_waking_respiration_value,
            highest_respiration_value=garmin_stat.highest_respiration_value,
            last_night_hrv=garmin_stat.last_night_hrv,
        )

    text = texts.statistics.format(
        date=date.strftime("%d.%m.%Y"),
        products=products_text,
        calories=int(total_calories),
        protein=int(total_protein),
        fats=int(total_fats),
        carbohydrates=int(total_carbohydrates),
        garmin_stat=garmin_stat_text,
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


def additional(update: Update, context: CallbackContext):
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

    wait_msg = update.message.reply_text(
        text=texts.garmin_wait,
        parse_mode=ParseMode.HTML,
    )

    if not check_garmin_credentials(garmin_username, garmin_password):
        wait_msg.delete()
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=texts.garmin_invalid_credentials,
            reply_markup=keyboards.home_menu(),
            parse_mode=ParseMode.HTML,
        )
        context.user_data["garmin_username"] = None

        return states.GARMIN_USERNAME

    user.garmin_login = encrypt_data(garmin_username)
    user.garmin_password = encrypt_data(garmin_password)
    user.save()

    wait_msg.delete()
    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.garmin_successfully_added,
        reply_markup=keyboards.user_menu(user),
        parse_mode=ParseMode.HTML,
    )

    return ConversationHandler.END


def delete_garmin_credentials(update: Update, context: CallbackContext):
    user = User.get_user(update)

    user.garmin_login = None
    user.garmin_password = None
    user.save()

    gaemin_synced_data = GarminSyncedData.objects.filter(user=user).delete()

    context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.garmin_credentials_deleted,
        reply_markup=keyboards.user_menu(user),
        parse_mode=ParseMode.HTML,
    )

    return start(update, context)


def convert_to_integer(input_str):
    numbers = re.findall(r"\d+", input_str)
    if len(numbers) == 1:
        return int(numbers[0])
    else:
        return None


def start_choose_meal(update: Update, context: CallbackContext):
    user = User.get_user(update)

    if not (update.message and update.message.text) and len(context.user_data.get("dishes_to_handle", [])) == 0:
        update.callback_query.edit_message_text(
            text=texts.user_error_message,
            reply_markup=keyboards.call_menu(),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    if len(context.user_data.get("dishes_to_handle", [])) != 0:
        data = context.user_data["dishes_to_handle"]

    elif update.message and update.message.text:
        data = update.message.text
        data = data.replace(";", "\n")
        data = data.replace(",", "\n")

        gram_words = [
            "граммов",
            "граммы",
            "грамма",
            "грамов",
            "грамм",
            "грама",
            "грам",
            "гр.",
            " гр",
            " г",
            " г.",
            "гр.",
        ]

        for word in gram_words:
            data = data.replace(word, "")

        data = data.replace("-", " ")

        data = data.strip().splitlines()

        data = list(map(lambda x: " ".join(x.split()), data))

        data = list(filter(lambda x: x, data))
        data = list(map(lambda x: x.strip(), data))

    try:
        text_time = data[0]
        formated_time = datetime.strptime(text_time, "%H:%M")
        now = datetime.now().date()
        context.user_data["group_time"] = datetime.combine(now, formated_time.time())
        text = data[1]
        context.user_data["dishes_to_handle"] = data[2:]
    except ValueError:
        text = data[0]
        context.user_data["dishes_to_handle"] = data[1:]

    if len(text.split()) > 1:
        if not (convert_to_integer(text.split()[-1]) is None):
            weight = convert_to_integer(text.split()[-1])
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

    if context.user_data.get("weight"):
        weight = int(context.user_data["weight"])

        if context.user_data.get("group_time"):
            return choose_meal_date(update, context)

        update.callback_query.edit_message_text(
            text=texts.choose_meal_date.format(title=dish.title, weight=weight),
            reply_markup=keyboards.choose_meal_date(),
            parse_mode=ParseMode.HTML,
        )
        return states.CHOOSE_MEAL_DATE

    update.callback_query.edit_message_text(
        text=texts.choose_meal_weight.format(title=dish.title),
        reply_markup=keyboards.cancel_button(),
        parse_mode=ParseMode.HTML,
    )

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

    weight = convert_to_integer(weight)

    if weight is None:
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

    if context.user_data.get("group_time"):
        parsed_date = context.user_data["group_time"]
    else:
        if update.callback_query:
            text_date = update.callback_query.data.split(":")[1]
        else:
            text_date = update.message.text

        if text_date == "today":
            parsed_date = datetime.now()
        elif text_date == "yesterday":
            parsed_date = datetime.now() - timedelta(days=1)
        elif text_date == "tommorow":
            parsed_date = datetime.now() + timedelta(days=1)
        else:
            date_formats = ["%H:%M", "%d.%m.%y", "%d.%m.%Y %H:%M"]
            parsed_date = None

            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(text_date, date_format)
                    if date_format == "%H:%M":
                        day = datetime.now().date()
                        parsed_date = datetime(
                            day.year,
                            day.month,
                            day.day,
                            parsed_date.hour,
                            parsed_date.minute,
                        )
                    break
                except ValueError:
                    pass

            else:
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

    meal = Meal(user=user, dish=dish, grams=weight, date_time=parsed_date)
    meal.save()

    text = texts.meal_added.format(title=dish.title, weight=meal.grams, date=meal.date_time)

    if update.callback_query:
        update.callback_query.edit_message_text(
            text=text,
            parse_mode=ParseMode.HTML,
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_user.id,
            text=text,
            reply_markup=keyboards.home_menu(),
            parse_mode=ParseMode.HTML,
        )

    dishes_to_handle = context.user_data.get("dishes_to_handle", [])
    context.user_data["weight"] = None

    if len(dishes_to_handle) == 0:
        return start(update, context)

    return start_choose_meal(update, context)


def delete_meal_start(update: Update, context: CallbackContext):
    user = User.get_user(update)

    date = context.user_data.get("date", datetime.now().date())
    meals = Meal.objects.filter(user=user, date_time__date=date).order_by("date_time")

    update.callback_query.edit_message_text(
        text=texts.delete_meal_start,
        reply_markup=keyboards.delete_meal_menu(meals),
        parse_mode=ParseMode.HTML,
    )

    return states.DELETE_MEAL


def delete_meal(update: Update, context: CallbackContext):
    user = User.get_user(update)

    meal_id = update.callback_query.data.split(":")[1]

    meal = Meal.objects.get(id=meal_id, user=user)

    meal.delete()

    update.callback_query.edit_message_text(
        text=texts.meal_deleted,
        parse_mode=ParseMode.HTML,
    )

    return statistics(update, context)


def sync_garmin(update: Update, context: CallbackContext):
    user = User.get_user(update)

    if not user.has_garmin_credentials:
        update.callback_query.edit_message_text(
            text=texts.garmin_not_connected,
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    wait_message = context.bot.send_message(
        chat_id=update.effective_user.id,
        text=texts.garmin_sync_wait,
        parse_mode=ParseMode.HTML,
    )

    from garminconnect import Garmin

    client = Garmin(user.garmin_plain_login, user.garmin_plain_password)
    client.login()
    today = datetime.now().date()

    stats = client.get_stats(today.isoformat())
    hrv_stats = client.get_hrv_data(today.isoformat())

    args = {
        "body_battery_charged_value": stats["bodyBatteryChargedValue"],
        "body_battery_drained_value": stats["bodyBatteryDrainedValue"],
        "body_battery_highest_value": stats["bodyBatteryHighestValue"],
        "resting_heart_rate": stats["restingHeartRate"],
        "max_avg_heart_rate": stats["maxAvgHeartRate"],
        "average_stress_level": stats["averageStressLevel"],
        "minutes_sleep": stats["sleepingSeconds"] // 60,
        "total_steps": stats["totalSteps"],
        "lowest_respiration_value": stats["lowestRespirationValue"],
        "avg_waking_respiration_value": stats["avgWakingRespirationValue"],
        "highest_respiration_value": stats["highestRespirationValue"],
        "last_night_hrv": hrv_stats["hrvSummary"]["lastNightAvg"],
    }

    garmin_stat = GarminSyncedData.objects.create(
        user=user,
        date_time=datetime.now(),
        **args,
    )

    wait_message.edit_text(
        text=texts.garmin_successfully_synced,
        parse_mode=ParseMode.HTML,
    )

    return statistics(update, context)

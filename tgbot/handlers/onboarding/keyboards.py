from typing import List
import time

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from diary.models import Dish, Meal

from users.models import User

from text_manager.models import button_texts


def t(text: str) -> str:
    return f"{text}:{time.time()}"


def user_menu(user: User) -> InlineKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(button_texts.home),
            KeyboardButton(button_texts.statistics),
        ],
        [
            KeyboardButton(button_texts.addtionals),
        ],
    ]

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def cancel_button() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(button_texts.cancel, callback_data=t("cancel")),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def additional_menu(user: User) -> InlineKeyboardMarkup:
    if user.has_garmin_credentials:
        buttons = [
            [
                KeyboardButton(button_texts.sync_garmin),
            ],
            [
                KeyboardButton(button_texts.delete_garmin_credentials),
            ],
            [
                KeyboardButton(button_texts.home),
            ],
        ]
    else:
        buttons = [
            [
                KeyboardButton(button_texts.add_garmin),
            ],
            [
                KeyboardButton(button_texts.home),
            ],
        ]

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def statistics_menu() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(button_texts.previous_day, callback_data=t("previous_day")),
            InlineKeyboardButton(button_texts.next_day, callback_data=t("next_day")),
        ],
        [
            InlineKeyboardButton(button_texts.specify_date, callback_data=t("specify_date")),
        ],
        [
            InlineKeyboardButton(button_texts.current_day, callback_data=t("current_day")),
        ],
        [
            InlineKeyboardButton(button_texts.delete_meal, callback_data=t("delete_meal")),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def delete_meal_menu(meals: List[Meal]) -> InlineKeyboardMarkup:
    buttons = []

    for meal in meals:
        buttons.append(
            [
                InlineKeyboardButton(f"[{meal.id}] {meal.dish.title[:50]} {meal.grams}", callback_data=t(f"delete_meal:{meal.id}")),
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(button_texts.cancel, callback_data=t("cancel")),
        ],
    )

    return InlineKeyboardMarkup(buttons)


def home_menu() -> ReplyKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(button_texts.home),
        ],
    ]

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)


def choose_meal(top):
    buttons = []

    for dish in top:
        dish: Dish = dish[0]
        buttons.append(
            [
                InlineKeyboardButton(dish.title, callback_data=t(f"choose_meal:{dish.id}")),
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(button_texts.cancel, callback_data=t("cancel")),
        ],
    )

    return InlineKeyboardMarkup(buttons)


def choose_meal_date() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                button_texts.today,
                callback_data=t(f"choose_meal_date:today"),
            ),
        ],
        [
            InlineKeyboardButton(
                button_texts.yesterday,
                callback_data=t(f"choose_meal_date:yesterday"),
            ),
            InlineKeyboardButton(
                button_texts.tomorrow,
                callback_data=t(f"choose_meal_date:tommorow"),
            ),
        ],
        [
            InlineKeyboardButton(
                button_texts.cancel,
                callback_data=t("cancel"),
            ),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def call_menu() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                button_texts.home,
                callback_data=t(f"cancel"),
            ),
        ],
    ]

    return InlineKeyboardMarkup(buttons)

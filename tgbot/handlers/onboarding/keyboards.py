from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup
from dtb import settings

from users.models import User

from typing import List

from text_manager.models import button_texts

import time


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


def statistics_menu() -> InlineKeyboardMarkup:
    buttons = [
        [
            KeyboardButton(button_texts.previous_day),
            KeyboardButton(button_texts.next_day),
        ],
        [
            KeyboardButton(button_texts.specify_date),
        ],
        [
            KeyboardButton(button_texts.current_day),
        ],
    ]

    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
from decimal import Decimal
import logging

from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ConversationHandler
from dtb import settings

from users.models import User
import tgbot.handlers.onboarding.keyboards as keyboards

from text_manager.models import texts

from tgbot import states


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

    user.is_active = True
    user.save()

    if user.is_first_time:
        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=texts.start_first_time,
            reply_markup=keyboards.user_menu(user),
            parse_mode=ParseMode.HTML,
            disable_web_page_preview=True,
        )

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


def statistics
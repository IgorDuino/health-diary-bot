from django.db import models


class MetaClass(type):
    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith("__"):
                attrs[attr_name] = AttributeDescriptor(attr_name, attr_value)
        return super().__new__(cls, name, bases, attrs)


class MetaClassButton(type):
    def __new__(cls, name, bases, attrs):
        for attr_name, attr_value in attrs.items():
            if not attr_name.startswith("__"):
                attrs[attr_name] = AttributeDescriptorButton(attr_name, attr_value)
        return super().__new__(cls, name, bases, attrs)


class AttributeDescriptor:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __get__(self, instance, owner):
        if instance is None:
            return self.value

        if Text.objects.filter(title=self.name).exists():
            return Text.objects.get(title=self.name).text
        else:
            new_text = Text(title=self.name, text=self.value)
            new_text.save()
            return new_text.text


class AttributeDescriptorButton:
    def __init__(self, name, value):
        self.name = name
        self.value = value

    def __get__(self, instance, owner):
        if instance is None:
            return self.value

        if ButtonText.objects.filter(title=self.name).exists():
            return ButtonText.objects.get(title=self.name).text
        else:
            new_text = ButtonText(title=self.name, text=self.value)
            new_text.save()
            return new_text.text


class ButtonTexts(metaclass=MetaClassButton):
    home = "Главная"
    statistics = "Статистика"
    addtionals = "Дополнительно"

    previous_day = "Предыдущий день"
    next_day = "Следующий день"
    specify_date = "Указать дату"
    current_day = "Статистика за сегодня"
    delete_meal = "Удалить приём пищи"

    add_garmin = "Добавить Garmin аккаунт"
    sync_garmin = "Синхронизировать с Garmin"
    delete_garmin_credentials = "Отвязать Garmin"

    cancel = "Отмена"
    yesterday = "Вчера"
    today = "Сегодня"
    tomorrow = "Завтра"


class Texts(metaclass=MetaClass):
    start_first_time = "😃Привет, друг!\nЯ твой личный дневник здоровья.\nПожалуйста, вводи информацию о своём питании.\n\nДля добавления приёма пищи введите название блюда и массу (опционально\nНапример 'Курица' или 'Курица 200', чтобы добавить сразу несколько блюд вводите каждое на отдельной строчке. например:\nКурица 200\nЯйцо 70\nХлеб 50"
    today_stat = "<b>Твоя краткая статистика за сегодня:</b>👇\n\nКалории: {calories} \nБелок: {protein}\nЖиры: {fats}\nУглеводы: {carbohydrates}"
    user_error_message = "🤔 Простите, произошла ошибка. Пожалуйста, попробуйте ещё раз."
    disabled_for_new_users = (
        "🤔 Простите, но в данный момент бот не принимает новых пользователей. Пожалуйста, попробуйте позже."
    )
    additional = "👇 Дополнительно 👇"

    statistics = "📊 Статистика за <b>{date}</b>:\n\n{products}\n<b>Общий итог:</b>\nКалории: {calories} \nБелок: {protein}\nЖиры: {fats}\nУглеводы: {carbohydrates}"
    product_stat = "<code>{name} {grams}г</code>:\n<i>Калории:</i> {calories} \n<i>Белок:</i> {protein}\n<i>Жиры:</i> {fats}\n<i>Углеводы:</i> {carbohydrates}\n\n"
    specify_date = "📅 Пожалуйста, введите дату в формате или <b>ДД.ММ</b> <b>ДД.ММ.ГГ</b>\n(например 05.06 (5 Июн) или 15.12.20 (15 Дек 2020 года))"

    delete_meal_start = "👇 Пожалуйста, выберите НОМЕР приёма пищи, который хотите удалить. Только число!"
    meal_deleted = "🗑 Приём пищи удалён"
    delete_meal_error = "🤔 Во время обработки запроса произошла ошибка. Возможная причина: введён неверный номер приёма пищи. Пожалуйста, попробуйте ещё раз."

    garmin_username = "👤 Пожалуйста, введите ваш логин от Garmin"
    garmin_password = "🔑 Пожалуйста, введите ваш пароль от Garmin"
    garmin_wait = "🕛 Пожалуйста, подождите, идёт добавление аккаунта Garmin"
    garmin_invalid_credentials = (
        "🤔 Простите, но введены неверные данные. Пожалуйста, попробуйте ещё раз.\n Введите ваш логин от Garmin"
    )
    garmin_successfully_added = "🎉 Поздравляем! Вы успешно добавили свой аккаунт Garmin. Теперь вы можете синхронизировать данные с вашего аккаунта Garmin."

    choose_meal = "<b>Добавление приёма пищи</b>\n\n'{name}'👇 Пожалуйста, выберите блюдо из списка"
    choose_meal_weight = "<b>Добавление приёма пищи</b>\n\n<u>Выбрано блюдо: {title}</u>\n\n👇 Пожалуйста, введите вес блюда в граммах (только число)"
    choose_meal_date = "<b>Добавление приёма пищи</b>\n\n<u>Выбрано блюдо: {title}</u>\n<u>Вес блюда: {weight}г</u>\n\n👇 Пожалуйста, введите дату в формате <b>ДД.ММ.ГГ ЧЧ:ММ </b>(24ч)\n(например 15.12.23 16:30) или выберите одну из дат на кнопках"
    meal_added = "🎉 Блюдо {title} {weight}г успешно добавлено!"


text_choices = [attr for attr in dir(Texts) if not attr.startswith("__")]
button_text_choices = [attr for attr in dir(ButtonTexts) if not attr.startswith("__")]


texts = Texts()
button_texts = ButtonTexts()


class Text(models.Model):
    class Meta:
        db_table = "text_table"

    title = models.CharField(
        max_length=255,
        choices=[(choice, choice) for choice in text_choices],
        unique=True,
        null=False,
        blank=False,
    )

    text = models.TextField(
        max_length=5000,
        null=False,
        blank=False,
    )


class ButtonText(models.Model):
    class Meta:
        db_table = "button_text_table"

    title = models.CharField(
        max_length=255,
        choices=[(choice, choice) for choice in button_text_choices],
        unique=True,
        null=False,
        blank=False,
    )

    text = models.TextField(
        max_length=5000,
        null=False,
        blank=False,
    )

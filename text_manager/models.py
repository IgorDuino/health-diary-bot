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
    current_day = "Текущий день"


class Texts(metaclass=MetaClass):
    start_first_time = "😃Привет, друг!\nЯ твой личный дневник здоровья.\nПожалуйста, вводи информацию о своём питании.\n\nМожно вводить просто название еды, либо указать по отдельности составляющие БЖУ.\n\nВвод через пробел, в формате:\nНазвание еды X Белок Y Жиры Z Углеводы A"
    today_stat = "<b>Твоя краткая статистика за сегодня:</b>👇\nКалории: {calories} \nБелок: {protein}\nЖиры: {fats}\nУглеводы: {carbohydrates}"
    user_error_message = "🤔 Простите, произошла ошибка. Пожалуйста, попробуйте ещё раз."
    disabled_for_new_users = "🤔 Простите, но в данный момент бот не принимает новых пользователей. Пожалуйста, попробуйте позже."

    statistics = "📊 Статистика за <b>{date}</b>:\n\n{products}\n\n<b>Общий итог:</b>\nКалории: {calories} \nБелок: {protein}\nЖиры: {fats}\nУглеводы: {carbohydrates}"
    specify_date = "📅 Пожалуйста, введите дату в формате <b>ДД.ММ.ГГ</b>\n(например 15.12.23)"
    

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

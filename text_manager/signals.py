from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def do_something_after_migrations(sender, **kwargs):
    from text_manager.models import (
        text_choices,
        Text,
        Texts,
        button_text_choices,
        ButtonText,
        ButtonTexts,
    )

    for choice in text_choices:
        if not Text.objects.filter(title=choice).exists():
            new_text = Text(title=choice, text=getattr(Texts, choice))
            new_text.save()

    for choice in button_text_choices:
        if not ButtonText.objects.filter(title=choice).exists():
            new_text = ButtonText(title=choice, text=getattr(ButtonTexts, choice))
            new_text.save()

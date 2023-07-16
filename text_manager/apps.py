from django.apps import AppConfig


class TextManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "text_manager"

    def ready(self):
        import sys

        if "makemigrations" in sys.argv:
            return

        import text_manager.signals

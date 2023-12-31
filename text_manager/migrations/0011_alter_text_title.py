# Generated by Django 4.2.1 on 2023-08-04 09:09

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("text_manager", "0010_alter_buttontext_title_alter_text_title"),
    ]

    operations = [
        migrations.AlterField(
            model_name="text",
            name="title",
            field=models.CharField(
                choices=[
                    ("additional", "additional"),
                    ("choose_meal", "choose_meal"),
                    ("choose_meal_date", "choose_meal_date"),
                    ("choose_meal_weight", "choose_meal_weight"),
                    ("delete_meal_error", "delete_meal_error"),
                    ("delete_meal_start", "delete_meal_start"),
                    ("disabled_for_new_users", "disabled_for_new_users"),
                    ("garmin_invalid_credentials", "garmin_invalid_credentials"),
                    ("garmin_not_connected", "garmin_not_connected"),
                    ("garmin_password", "garmin_password"),
                    ("garmin_stat", "garmin_stat"),
                    ("garmin_successfully_added", "garmin_successfully_added"),
                    ("garmin_sync_wait", "garmin_sync_wait"),
                    ("garmin_username", "garmin_username"),
                    ("garmin_wait", "garmin_wait"),
                    ("meal_added", "meal_added"),
                    ("meal_deleted", "meal_deleted"),
                    ("product_stat", "product_stat"),
                    ("specify_date", "specify_date"),
                    ("start_first_time", "start_first_time"),
                    ("statistics", "statistics"),
                    ("today_stat", "today_stat"),
                    ("user_error_message", "user_error_message"),
                ],
                max_length=255,
                unique=True,
            ),
        ),
    ]

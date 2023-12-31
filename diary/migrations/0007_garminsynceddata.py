# Generated by Django 4.2.1 on 2023-08-04 09:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_user_garmin_login_user_garmin_password"),
        ("diary", "0006_alter_meal_options_meal_date_time_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="GarminSyncedData",
            fields=[
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("date", models.DateField()),
                ("body_battery_charged_value", models.PositiveIntegerField(null=True)),
                ("body_battery_drained_value", models.PositiveIntegerField(null=True)),
                ("body_battery_highest_value", models.PositiveIntegerField(null=True)),
                ("resting_heart_rate", models.PositiveIntegerField(null=True)),
                ("max_avg_heart_rate", models.PositiveIntegerField(null=True)),
                ("average_stress_level", models.PositiveIntegerField(null=True)),
                ("hour_sleep", models.PositiveIntegerField(null=True)),
                ("minutes_sleep", models.PositiveIntegerField(null=True)),
                ("total_steps", models.PositiveIntegerField(null=True)),
                ("lowest_respiration_value", models.PositiveIntegerField(null=True)),
                (
                    "avg_waking_respiration_value",
                    models.PositiveIntegerField(null=True),
                ),
                ("highest_respiration_value", models.PositiveIntegerField(null=True)),
                (
                    "user",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="users.user"),
                ),
            ],
        ),
    ]

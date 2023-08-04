# Generated by Django 4.2.1 on 2023-08-04 16:21

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("diary", "0007_garminsynceddata"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="garminsynceddata",
            name="date",
        ),
        migrations.RemoveField(
            model_name="garminsynceddata",
            name="hour_sleep",
        ),
        migrations.AddField(
            model_name="garminsynceddata",
            name="date_time",
            field=models.DateTimeField(default=datetime.datetime(2023, 8, 4, 16, 21, 36, 849251)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="garminsynceddata",
            name="last_night_hrv",
            field=models.PositiveIntegerField(null=True),
        ),
    ]
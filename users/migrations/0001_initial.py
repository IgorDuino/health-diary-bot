# Generated by Django 4.2.1 on 2023-07-16 14:05

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("created_at", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("id", models.AutoField(primary_key=True, serialize=False)),
                ("user_id", models.CharField(max_length=32, unique=True)),
                ("username", models.CharField(blank=True, max_length=32, null=True)),
                ("first_name", models.CharField(max_length=256)),
                ("last_name", models.CharField(blank=True, max_length=256, null=True)),
                (
                    "language_code",
                    models.CharField(blank=True, default="ru", max_length=8, null=True),
                ),
                ("deep_link", models.CharField(blank=True, max_length=64, null=True)),
                ("is_blocked_bot", models.BooleanField(default=False)),
                ("is_admin", models.BooleanField(default=False)),
                ("is_first_time", models.BooleanField(default=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={
                "ordering": ("-created_at",),
                "abstract": False,
            },
        ),
    ]

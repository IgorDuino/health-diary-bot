from django.db import models
from utils.models import CreateTracker
from django.core.validators import MinValueValidator


class Dish(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    grams = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    calories = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    protein = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    fats = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    carbohydrates = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])

    @property
    def cal(self):
        return self.calories / self.grams

    @property
    def prot(self):
        return self.protein / self.grams

    @property
    def fat(self):
        return self.fats / self.grams

    @property
    def carb(self):
        return self.carbohydrates / self.grams

    def __str__(self):
        return self.title


class Meal(CreateTracker):
    id = models.AutoField(primary_key=True)
    dish = models.ForeignKey("diary.Dish", on_delete=models.CASCADE)
    grams = models.PositiveIntegerField()
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    date_time = models.DateTimeField()

    def __str__(self):
        return f"{self.dish.title} - {self.grams}г"


class GarminSyncedData(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    date = models.DateField()

    body_battery_charged_value = models.PositiveIntegerField(null=True)
    body_battery_drained_value = models.PositiveIntegerField(null=True)
    body_battery_highest_value = models.PositiveIntegerField(null=True)

    resting_heart_rate = models.PositiveIntegerField(null=True)
    max_avg_heart_rate = models.PositiveIntegerField(null=True)

    average_stress_level = models.PositiveIntegerField(null=True)

    hour_sleep = models.PositiveIntegerField(null=True)
    minutes_sleep = models.PositiveIntegerField(null=True)

    total_steps = models.PositiveIntegerField(null=True)

    lowest_respiration_value = models.PositiveIntegerField(null=True)
    avg_waking_respiration_value = models.PositiveIntegerField(null=True)
    highest_respiration_value = models.PositiveIntegerField(null=True)

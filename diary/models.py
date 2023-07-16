from django.db import models
from utils.models import CreateTracker
from django.core.validators import MinValueValidator


class Dish(models.Model):
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
    dish = models.ForeignKey("diary.Dish", on_delete=models.CASCADE)
    grams = models.PositiveIntegerField()
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.title
